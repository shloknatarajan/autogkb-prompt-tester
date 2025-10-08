import React from 'react'

export default function OutputsSidebar({ prompts, onSavePrompt, onSaveAll }) {
  return (
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
        onClick={onSaveAll}
        disabled={prompts.length === 0}
        className="save-all-btn"
      >
        Save All Prompts
      </button>
    </div>
  )
}
