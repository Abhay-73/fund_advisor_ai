# Fund Advisor AI: Multi-Agent Financial Advisor

FundFlow is an Agentic AI application that automates mutual fund analysis. It employs a **Multi-Agent System (MAS)** where autonomous agents (Scout, Quant, Advisor) collaborate to fetch live market data, calculate risk metrics (CAGR, Volatility), and generate personalized investment recommendations.


## Tech Stack
- **Backend:** Python, FastAPI, CrewAI (Multi-Agent Orchestration), Pandas, Google Gemini Flash.
- **Frontend:** React (Vite), Axios, React-Markdown.
- **Agentic Patterns:** ReAct (Reason+Act), Tool Use (Function Calling), Role-Playing.

## Architecture
The system consists of three specialized agents:
1.  **Market Scout:** Fetches historical NAV data from the AMFI API.
2.  **Quant Analyst:** Executes local Python code (pandas) to calculate financial metrics like Alpha, Beta, and Volatility.
3.  **Financial Advisor:** Synthesizes technical data into human-readable investment advice.

```mermaid
graph TD
    subgraph Frontend ["Frontend (React)"]
        UI[User Interface] -->|POST /analyze| API
    end

    subgraph Backend ["Backend (FastAPI + CrewAI)"]
        API[FastAPI Endpoint] -->|Trigger| Crew[Agent Crew]
        
        subgraph Agents ["The Agent Team"]
            Scout[Scout Agent]
            Quant[Quant Agent]
            Advisor[Advisor Agent]
        end
        
        Crew --> Scout
        Scout -->|Pass CSV| Quant
        Quant -->|Pass Metrics| Advisor
    end

    subgraph Tools ["External Tools"]
        Scout -->|Fetch NAV| AMFI[AMFI API]
        Quant -->|Calc Risk| Python[Python REPL (Pandas)]
    end

    Advisor -->|Return Email| API
    API -->|JSON Response| UI
```
    
## Installation

### Backend
```bash
cd backend
python -m venv venv
# Activate venv
pip install -r requirements.txt
python api.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## NOTE
This project uses Google Gemini API (Free Tier). Due to rate limits (15 RPM), the agents are throttled (max_rpm=10) to prevent crashing.
