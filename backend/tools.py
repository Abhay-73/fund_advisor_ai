import pandas as pd
from crewai.tools import BaseTool
from mftool import Mftool
from langchain_experimental.tools import PythonREPLTool

class FundDataTool(BaseTool):
    name: str = "Fetch Mutual Fund Data"
    description: str = (
        "Fetches the last 3 years of NAV history for a given AMFI Scheme Code "
        "and saves it to a CSV file. Returns the filename. "
        "Input: String code like '120503'."
    )

    def _run(self, scheme_code: str) -> str:
        mf = Mftool()
        try:
            # 1. Fetch data
            data = mf.get_scheme_historical_nav(scheme_code, as_Dataframe=False)
            
            # 2. Convert to DataFrame
            df = pd.DataFrame(data['data'])
            
            # 3. DATA CLEANING (The Fix for NaN)
            # Convert NAV to numeric, forcing errors to NaN (then dropping them)
            df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
            
            # Convert Date and SORT ASCENDING (Oldest -> Newest)
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df = df.sort_values(by='date', ascending=True)
            
            # Drop any garbage rows
            df = df.dropna()
            
            # 4. Save to local disk
            filename = "fund_data.csv"
            df.to_csv(filename, index=False)
            
            return f"Success: Data saved to '{filename}' with {len(df)} rows. Columns: date, nav. Tell the Quant to read this."
        except Exception as e:
            return f"Error: {str(e)}"

class LocalPythonTool(BaseTool):
    name: str = "Python Analyst"
    description: str = (
        "Executes Python code. "
        "IMPORTANT: To analyze data, you must read the CSV file 'fund_data.csv'. "
        "1. Calculate 'daily_return' = nav.pct_change() * 100. "
        "2. REQUIRED: Run 'df.dropna(inplace=True)' immediately after pct_change() "
        "   to remove the first row, otherwise Volatility will be NaN. "
        "3. Calculate annualized volatility = daily_return.std() * (252 ** 0.5)."
    )

    def _run(self, code: str) -> str:
        try:
            python_repl = PythonREPLTool()
            return python_repl.run(code)
        except Exception as e:
            return f"Error executing code: {str(e)}"