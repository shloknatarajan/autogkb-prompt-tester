import React from 'react'

const MODELS = [
  'gpt-4o',
  'gpt-4o-mini',
  'gpt-4-turbo',
  'gpt-4',
  'gpt-3.5-turbo'
]

export default function PromptDetails({ prompt, onUpdate, onRun }) {
  return (
    <div className="prompt-details">
      <h3>Configure Prompt</h3>
      <div className="form-group">
        <label htmlFor="model">Model:</label>
        <select
          id="model"
          value={prompt.model}
          onChange={(e) => onUpdate('model', e.target.value)}
        >
          {MODELS.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>

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
