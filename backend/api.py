from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process, LLM
from tools import FundDataTool, LocalPythonTool
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins 
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods 
    allow_headers=["*"],
)

# Input Schema
class FundRequest(BaseModel):
    scheme_code: str # e.g., "120503"



@app.post("/analyze")
def run_analysis(request: FundRequest):
    try:
        # 1. SETUP LLM (First)
        my_llm = LLM(
            model="gemini/gemini-flash-latest",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.5
        )

        # 2. DEFINE AGENTS 
        scout = Agent(
            role='Market Data Scout',
            goal='Retrieve accurate historical data',
            backstory="Data engineer.",
            tools=[FundDataTool()],
            llm=my_llm,
            verbose=True
        )

        quant = Agent(
            role='Quantitative Analyst',
            goal='Calculate CAGR and Volatility',
            backstory="Financial analyst.",
            tools=[LocalPythonTool()],
            llm=my_llm,
            verbose=True
        )

        advisor = Agent(
            role='Financial Advisor',
            goal='Write recommendation',
            backstory="Wealth manager.",
            llm=my_llm,
            verbose=True
        )

        # 3. DEFINE TASKS
        task_fetch = Task(
            description=f"Fetch 5 years of data for Scheme {request.scheme_code} and save to CSV.",
            expected_output="File saved confirmation.",
            agent=scout 
        )

        task_analyze = Task(
            description="""
            Write Python code to analyze 'fund_data.csv'. 
            FOLLOW THESE STEPS STRICTLY TO AVOID 'NaN' ERRORS:
            
            1. Read CSV: df = pd.read_csv('fund_data.csv')
            2. CLEANING (Critical):
               - Convert nav to numeric: df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
               - Filter Zeros: df = df[df['nav'] > 0.01] 
               - Drop NaNs: df.dropna(inplace=True)
            
            3. CALCULATE RETURNS:
               - df['pct'] = df['nav'].pct_change()
               - Clean Infinite values: df.replace([float('inf'), -float('inf')], float('nan'), inplace=True)
               - Drop NaNs again: df.dropna(inplace=True) 

            4. CALCULATE METRICS:
               - Years = (pd.to_datetime(df['date'].iloc[-1]) - pd.to_datetime(df['date'].iloc[0])).days / 365.25
               - CAGR: ((df['nav'].iloc[-1] / df['nav'].iloc[0]) ** (1/Years)) - 1
               - Volatility: df['pct'].std() * (252 ** 0.5)
               - Sharpe: (CAGR - 0.06) / Volatility
               - Drawdown: 
                 rolling_max = df['nav'].cummax()
                 dd = (df['nav'] - rolling_max) / rolling_max
                 max_dd = dd.min()
            
            5. PRINT RESULT:
               CAGR: X.XX%
               Volatility: X.XX%
               Sharpe: X.XX
               Drawdown: X.XX%
            """,
            expected_output="Financial Metrics printed to console.",
            agent=quant
        )
        task_advise = Task(
            description="""
            Analyze the metrics provided by the Quant.
            
            1. Determine Investment Horizon:
               - If Volatility > 15% OR Drawdown < -20%: "LONG TERM ONLY (>5 Yrs)"
               - If Volatility < 8%: "SHORT/MID TERM"
               - Otherwise: "MID TERM (3-5 Yrs)".
            
            2. Verdict:
               - If Sharpe > 1.0: "GOOD BUY"
               - If Sharpe < 0.5: "CAUTION / AVOID"
               - Else: "NEUTRAL"

            3. Final Output Format:
               Create a Markdown Table with columns: Metric, Value, Meaning.
               Add **VERDICT** and **RECOMMENDED HORIZON** at the bottom.
            """,
            expected_output="Markdown table and horizon recommendation.",
            agent=advisor
        )

        # 4. ASSEMBLE CREW
        crew = Crew(
            agents=[scout, quant, advisor],
            tasks=[task_fetch, task_analyze, task_advise],
            process=Process.sequential,
            max_rpm=10
        )

        result = crew.kickoff()
        return {"result": str(result)}

    except Exception as e:
        # Print error to terminal for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
