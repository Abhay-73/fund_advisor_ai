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
        # 1. Setup Crew (same as main.py)
        my_llm = LLM(
            model="gemini/gemini-flash-lite-latest",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.5
        )

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

        # 2. Define Tasks Dynamicallly
        task_fetch = Task(
            description=f"Fetch data for Scheme {request.scheme_code} and save to CSV.",
            expected_output="File saved confirmation.",
            agent=scout
        )

        task_analyze = Task(
            description="Read CSV. Calculate CAGR and Volatility. Drop NaNs before calc.",
            expected_output="Metrics printed.",
            agent=quant
        )

        task_advise = Task(
            description="Write a recommendation letter based on the metrics.",
            expected_output="Final email text.",
            agent=advisor
        )

        crew = Crew(
            agents=[scout, quant, advisor],
            tasks=[task_fetch, task_analyze, task_advise],
            process=Process.sequential,
            max_rpm=10
        )

        # 3. Run
        result = crew.kickoff()
        
        return {"result": str(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)