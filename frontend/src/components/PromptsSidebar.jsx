import React from 'react'

export default function PromptsSidebar({
  prompts,
  selectedTask,
  selectedPromptIndex,
  onSelectPrompt,
  onAddPrompt,
  onUpdatePrompt,
  onDeletePrompt,
  onRunAll,
  loading
}) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>{selectedTask}</h3>
        <button onClick={onAddPrompt} className="add-btn">+ Add</button>
      </div>
      <div className="prompts-list">
        {prompts.map((prompt, index) => (
          <div
            key={prompt.id}
            className={`prompt-item ${selectedPromptIndex === index ? 'selected' : ''}`}
            onClick={() => onSelectPrompt(index)}
          >
            <div className="prompt-item-header">
              <input
                type="text"
                value={prompt.name}
                onChange={(e) => {
                  e.stopPropagation()
                  onUpdatePrompt(index, 'name', e.target.value)
                }}
                onClick={(e) => e.stopPropagation()}
                className="prompt-name-input"
              />
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDeletePrompt(index)
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
        onClick={onRunAll}
        disabled={loading || prompts.length === 0}
        className="run-all-btn"
      >
        {loading ? 'Running All...' : 'Run All Prompts'}
      </button>
    </div>
  )
}
