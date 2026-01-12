import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM 
from tools import FundDataTool, LocalPythonTool

# 1. Load Environment
load_dotenv()

# 2. Configure Gemini using CrewAI's native LLM class

my_llm = LLM(
    model="gemini/gemini-flash-lite-latest", # Note: We use the 'gemini/' prefix so CrewAI knows which provider to use.
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.5
)

# 3. Instantiate Tools
fetch_tool = FundDataTool()
quant_tool = LocalPythonTool()

# 4. Define Agents
scout = Agent(
    role='Market Data Scout',
    goal='Retrieve accurate historical data for Indian Mutual Funds',
    backstory="You are a data engineer. You fetch raw NAV data using AMFI codes.",
    tools=[fetch_tool],
    llm=my_llm,  
    verbose=True
)

quant = Agent(
    role='Quantitative Analyst',
    goal='Calculate CAGR and Volatility using Python',
    backstory="You are a financial analyst. You write Python scripts to analyze risk. "
              "You always verify your code before running it.",
    tools=[quant_tool],
    llm=my_llm,
    verbose=True
)

advisor = Agent(
    role='Financial Advisor',
    goal='Write a clear investment recommendation',
    backstory="You are a wealth manager. You explain complex metrics to beginners.",
    llm=my_llm,
    verbose=True
)

# 5. Define Tasks
fund_code = "120503" # Axis Bluechip Fund

task_fetch = Task(
    description=f"Fetch 3 years of data for Scheme {fund_code} and SAVE it to a CSV file.",
    expected_output="Confirmation that the file 'fund_data.csv' has been saved.",
    agent=scout
)

task_analyze = Task(
    description="""
    1. Write a Python script to READ 'fund_data.csv' using pandas.
    2. Calculate CAGR (Compound Annual Growth Rate) and Volatility.
    3. PRINT the results.
    """,
    expected_output="CAGR and Volatility values printed to console.",
    agent=quant
)

task_advise = Task(
    description="""
    Based on the CAGR and Volatility provided by the Quant, write a short 
    recommendation letter to the user. Explain if the risk is high or low.
    """,
    expected_output="A friendly investment recommendation email.",
    agent=advisor
)

# 6. Assemble Crew with Rate Limiting
fund_crew = Crew(
    agents=[scout, quant, advisor],
    tasks=[task_fetch, task_analyze, task_advise],
    process=Process.sequential,
    max_rpm=10 
)

# 7. Run
print("### Starting FundFlow Agent Crew ###")
result = fund_crew.kickoff()
print("\n\n########################")
print("## FINAL RECOMMENDATION ##")
print("########################\n")
print(result)