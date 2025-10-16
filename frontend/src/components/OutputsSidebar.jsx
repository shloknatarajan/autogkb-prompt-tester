import React from 'react'

export default function OutputsSidebar({ prompts, selectedTask, onSavePrompt, onSaveAll, onRunAll, onRunBest, bestPrompts, loading, tasks }) {
  return (
    <div className="outputs-sidebar">
      <div className="sidebar-header">
        <h3>Outputs - {selectedTask}</h3>
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
                  <button onClick={() => onSavePrompt(index)} className="save-output-btn">
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
      <button
        onClick={onRunAll}
        disabled={loading || prompts.length === 0}
        className="run-all-btn"
      >
        {loading ? 'Running All...' : 'Run All Prompts'}
      </button>
      <button
        onClick={onRunBest}
        disabled={loading || Object.keys(bestPrompts).length !== tasks.length}
        className="run-best-btn"
        title={Object.keys(bestPrompts).length !== tasks.length ? 'Select best prompt for all tasks first' : ''}
      >
        {loading ? 'Running Best...' : 'Run Best Prompts'}
      </button>
    </div>
  )
}
