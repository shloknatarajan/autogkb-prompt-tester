import React from 'react'

export default function PromptDetails({ prompt, onUpdate, onRun }) {
  return (
    <div className="prompt-details">
      <h3>Configure Prompt</h3>

      <div className="form-group">
        <label htmlFor="response-format">Response Format (JSON Schema):</label>
        <textarea
          id="response-format"
          value={prompt.responseFormat}
          onChange={(e) => onUpdate('responseFormat', e.target.value)}
          placeholder='Optional: Enter JSON response format'
          rows={3}
        />
      </div>

      <div className="form-group">
        <label htmlFor="prompt">Prompt:</label>
        <textarea
          id="prompt"
          value={prompt.prompt}
          onChange={(e) => onUpdate('prompt', e.target.value)}
          placeholder="Enter your prompt here..."
          rows={4}
        />
      </div>

      <button
        onClick={onRun}
        disabled={prompt.loading}
      >
        {prompt.loading ? 'Running...' : 'Run This Prompt'}
      </button>
    </div>
  )
}
