import { useState } from 'react'
import './App.css'

function App() {
  const [prompt, setPrompt] = useState('')
  const [text, setText] = useState('')
  const [model, setModel] = useState('gpt-4o-mini')
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const models = [
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-4-turbo',
    'gpt-4',
    'gpt-3.5-turbo'
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setOutput('')

    try {
      const response = await fetch('http://localhost:8000/test-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          text,
          model
        })
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()
      setOutput(data.output)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <h1>Prompt Tester</h1>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="model">Model:</label>
          <select
            id="model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            {models.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="prompt">Prompt:</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your prompt here..."
            rows={4}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="text">Text:</label>
          <textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter the text to process..."
            rows={6}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Test Prompt'}
        </button>
      </form>

      {error && (
        <div className="error">
          <h3>Error:</h3>
          <p>{error}</p>
        </div>
      )}

      {output && (
        <div className="output">
          <h3>Output:</h3>
          <pre>{output}</pre>
        </div>
      )}
    </div>
  )
}

export default App
