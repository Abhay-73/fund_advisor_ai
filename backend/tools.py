import pandas as pd
import numpy as np
from crewai.tools import BaseTool
from mftool import Mftool
from langchain_experimental.tools import PythonREPLTool

class FundDataTool(BaseTool):
    name: str = "Fetch Mutual Fund Data"
    description: str = (
        "Fetches the last 5 years of NAV history for a scheme code and saves 'fund_data.csv'. "
        "Input: Scheme Code (e.g. '120503')."
    )

    def _run(self, scheme_code: str) -> str:
        mf = Mftool()
        try:
            # Fetch data (Try 5 years for better long-term analysis)
            data = mf.get_scheme_historical_nav(scheme_code, as_Dataframe=False)
            df = pd.DataFrame(data['data'])
            
            df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df = df.sort_values(by='date', ascending=True) # Oldest to Newest
            
            df.to_csv("fund_data.csv", index=False)
            return "Data saved to 'fund_data.csv'. Ready for analysis."
        except Exception as e:
            return f"Error: {str(e)}"

class LocalPythonTool(BaseTool):
    name: str = "Python Analyst"
    description: str = (
        "Executes Python code. "
        "Use this to calculate CAGR, Volatility, Sharpe Ratio, and Max Drawdown. "
        "Input: Valid Python code string. "
    )

    def _run(self, code: str) -> str:
        
        try:
            python_repl = PythonREPLTool()
            return python_repl.run(code)
        except Exception as e:
            return f"Error executing code: {str(e)}"
