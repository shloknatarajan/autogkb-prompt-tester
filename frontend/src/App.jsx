import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [prompts, setPrompts] = useState([])
  const [selectedPromptIndex, setSelectedPromptIndex] = useState(null)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const models = [
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-4-turbo',
    'gpt-4',
    'gpt-3.5-turbo'
  ]

  const addNewPrompt = () => {
    const newPrompt = {
      id: Date.now(),
      name: `Prompt ${prompts.length + 1}`,
      prompt: '',
      model: 'gpt-4o-mini',
      responseFormat: '',
      output: null,
      loading: false
    }
    setPrompts([...prompts, newPrompt])
    setSelectedPromptIndex(prompts.length)
  }

  const updatePrompt = (index, field, value) => {
    const updated = [...prompts]
    updated[index][field] = value
    setPrompts(updated)
  }

  const runPrompt = async (index) => {
    const prompt = prompts[index]
    updatePrompt(index, 'loading', true)
    setError('')

    try {
      let parsedResponseFormat = null
      if (prompt.responseFormat?.trim()) {
        try {
          parsedResponseFormat = JSON.parse(prompt.responseFormat)
        } catch (err) {
          setError('Invalid JSON in response format: ' + err.message)
          updatePrompt(index, 'loading', false)
          return
        }
      }

      const response = await fetch('http://localhost:8000/test-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.prompt,
          text,
          model: prompt.model,
          response_format: parsedResponseFormat
        })
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()
      updatePrompt(index, 'output', data.output)
    } catch (err) {
      setError(err.message)
    } finally {
      updatePrompt(index, 'loading', false)
    }
  }

  const runAllPrompts = async () => {
    setLoading(true)
    for (let i = 0; i < prompts.length; i++) {
      await runPrompt(i)
    }
    setLoading(false)
  }

  const savePrompt = async (index) => {
    const prompt = prompts[index]
    try {
      const response = await fetch('http://localhost:8000/save-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.prompt,
          text,
          model: prompt.model,
          response_format: prompt.responseFormat ? JSON.parse(prompt.responseFormat) : null,
          output: prompt.output
        })
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()
      alert(data.message)
    } catch (err) {
      alert('Failed to save: ' + err.message)
    }
  }

  const deletePrompt = (index) => {
    const updated = prompts.filter((_, i) => i !== index)
    setPrompts(updated)
    if (selectedPromptIndex === index) {
      setSelectedPromptIndex(null)
    } else if (selectedPromptIndex > index) {
      setSelectedPromptIndex(selectedPromptIndex - 1)
    }
  }

  return (
    <div className="app">
      <h1>Prompt Tester</h1>

      <div className="container">
        <div className="sidebar">
          <div className="sidebar-header">
            <h3>Prompts</h3>
            <button onClick={addNewPrompt} className="add-btn">+ Add</button>
          </div>
          <div className="prompts-list">
            {prompts.map((prompt, index) => (
              <div
                key={prompt.id}
                className={`prompt-item ${selectedPromptIndex === index ? 'selected' : ''}`}
                onClick={() => setSelectedPromptIndex(index)}
              >
                <div className="prompt-item-header">
                  <input
                    type="text"
                    value={prompt.name}
                    onChange={(e) => {
                      e.stopPropagation()
                      updatePrompt(index, 'name', e.target.value)
                    }}
                    onClick={(e) => e.stopPropagation()}
                    className="prompt-name-input"
                  />
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      deletePrompt(index)
                    }}
                    className="delete-btn"
                  >
                    ×
                  </button>
                </div>
                {prompt.output && <span className="status-indicator">✓</span>}
              </div>
            ))}
          </div>
          <button
            onClick={runAllPrompts}
            disabled={loading || prompts.length === 0}
            className="run-all-btn"
          >
            {loading ? 'Running All...' : 'Run All Prompts'}
          </button>
        </div>

        <div className="main-content">
          <div className="text-section">
            <div className="form-group">
              <label htmlFor="text">Input Text:</label>
              <textarea
                id="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter the text to process..."
                rows={6}
              />
            </div>
          </div>

          {selectedPromptIndex !== null && prompts[selectedPromptIndex] && (
            <div className="prompt-details">
              <h3>Configure Prompt</h3>
              <div className="form-group">
                <label htmlFor="model">Model:</label>
                <select
                  id="model"
                  value={prompts[selectedPromptIndex].model}
                  onChange={(e) => updatePrompt(selectedPromptIndex, 'model', e.target.value)}
                >
                  {models.map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="response-format">Response Format (JSON Schema):</label>
                <textarea
                  id="response-format"
                  value={prompts[selectedPromptIndex].responseFormat}
                  onChange={(e) => updatePrompt(selectedPromptIndex, 'responseFormat', e.target.value)}
                  placeholder='Optional: Enter JSON response format'
                  rows={3}
                />
              </div>

              <div className="form-group">
                <label htmlFor="prompt">Prompt:</label>
                <textarea
                  id="prompt"
                  value={prompts[selectedPromptIndex].prompt}
                  onChange={(e) => updatePrompt(selectedPromptIndex, 'prompt', e.target.value)}
                  placeholder="Enter your prompt here..."
                  rows={4}
                />
              </div>

              <button
                onClick={() => runPrompt(selectedPromptIndex)}
                disabled={prompts[selectedPromptIndex].loading}
              >
                {prompts[selectedPromptIndex].loading ? 'Running...' : 'Run This Prompt'}
              </button>

              {prompts[selectedPromptIndex].output && (
                <div className="output">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4>Output:</h4>
                    <button onClick={() => savePrompt(selectedPromptIndex)}>
                      Save Prompt
                    </button>
                  </div>
                  <pre>{prompts[selectedPromptIndex].output}</pre>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="error">
              <h3>Error:</h3>
              <p>{error}</p>
            </div>
          )}
        </div>

        <div className="outputs-sidebar">
          <div className="sidebar-header">
            <h3>All Outputs</h3>
          </div>
          <div className="outputs-list">
            {prompts.length === 0 ? (
              <div className="empty-state">No prompts added yet</div>
            ) : (
              prompts.map((prompt, index) => (
                <div key={prompt.id} className="output-item">
                  <div className="output-item-header">
                    <strong>{prompt.name}</strong>
                    {prompt.loading && <span className="loading-indicator">⏳</span>}
                    {prompt.output && !prompt.loading && (
                      <button onClick={() => savePrompt(index)} className="save-output-btn">
                        Save
                      </button>
                    )}
                  </div>
                  {prompt.output ? (
                    <pre className="output-preview">{prompt.output}</pre>
                  ) : (
                    <div className="no-output">No output yet</div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
