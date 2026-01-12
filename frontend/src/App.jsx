import { useState } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import './App.css'

function App() {
  const [schemeCode, setSchemeCode] = useState('120503') // Default: Axis Bluechip
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    setResult('');
    
    try {
      // Connect to FastAPI backend
      const response = await axios.post('http://localhost:8000/analyze', {
        scheme_code: schemeCode
      });
      
      // The API returns { result: "..." }
      setResult(response.data.result);
    } catch (err) {
      setError('Analysis failed. Is the backend running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Funds Advisor AI</h1>
        <p>Multi-Agent Mutual Fund Advisor</p>
      </header>

      <div className="input-group">
        <input 
          type="text" 
          value={schemeCode}
          onChange={(e) => setSchemeCode(e.target.value)}
          placeholder="Enter AMFI Code (e.g., 120503)"
        />
        <button onClick={handleAnalyze} disabled={loading}>
          {loading ? 'Agents Working...' : 'Analyze Fund'}
        </button>
      </div>

      {loading && (
        <div className="status-box">
          <p>📡 <b>Scout</b> is fetching 3 years of data...</p>
          <p>📊 <b>Quant</b> is calculating Alpha & Beta...</p>
          <p>✍️ <b>Advisor</b> is drafting your letter...</p>
        </div>
      )}

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className="result-box">
          <ReactMarkdown>{result}</ReactMarkdown>
        </div>
      )}
    </div>
  )
}

export default App