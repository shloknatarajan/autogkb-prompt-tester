import React, { useState } from 'react'

export default function PromptsSidebar({
  prompts,
  tasks,
  selectedTask,
  selectedPromptIndex,
  onSelectPrompt,
  onAddPrompt,
  onUpdatePrompt,
  onDeletePrompt,
  onRunAll,
  onSelectTask,
  onAddTask,
  onDeleteTask,
  onRenameTask,
  loading
}) {
  const [showTaskManager, setShowTaskManager] = useState(false)
  const [isAddingTask, setIsAddingTask] = useState(false)
  const [newTaskName, setNewTaskName] = useState('')
  const [editingTask, setEditingTask] = useState(null)
  const [editedName, setEditedName] = useState('')

  const handleAddTask = () => {
    if (newTaskName.trim()) {
      onAddTask(newTaskName.trim())
      setNewTaskName('')
      setIsAddingTask(false)
    }
  }

  const handleRenameTask = (oldName) => {
    if (editedName.trim() && editedName !== oldName) {
      onRenameTask(oldName, editedName.trim())
    }
    setEditingTask(null)
    setEditedName('')
  }

  const startEditing = (task) => {
    if (task !== 'Default') {
      setEditingTask(task)
      setEditedName(task)
    }
  }

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>Prompts</h3>
      </div>

      <div className="task-selector">
        <select
          value={selectedTask}
          onChange={(e) => onSelectTask(e.target.value)}
          className="task-dropdown"
        >
          {tasks.map(task => (
            <option key={task} value={task}>{task}</option>
          ))}
        </select>
        <button
          onClick={() => setShowTaskManager(!showTaskManager)}
          className="manage-tasks-btn"
          title="Manage tasks"
        >
          ⋯
        </button>
      </div>

      {showTaskManager && (
        <div className="task-manager">
          <div className="task-manager-header">
            <strong>Manage Tasks</strong>
            <button
              onClick={() => setShowTaskManager(false)}
              className="close-btn"
            >
              ×
            </button>
          </div>
          <div className="task-manager-list">
            {tasks.map((task) => (
              <div key={task} className="task-manager-item">
                {editingTask === task ? (
                  <input
                    type="text"
                    value={editedName}
                    onChange={(e) => setEditedName(e.target.value)}
                    onBlur={() => handleRenameTask(task)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleRenameTask(task)
                      }
                    }}
                    className="task-name-input"
                    autoFocus
                  />
                ) : (
                  <>
                    <span
                      className="task-name"
                      onDoubleClick={() => startEditing(task)}
                    >
                      {task}
                    </span>
                    {task !== 'Default' && (
                      <button
                        onClick={() => {
                          if (confirm(`Delete task "${task}" and all its prompts?`)) {
                            onDeleteTask(task)
                          }
                        }}
                        className="delete-btn"
                      >
                        ×
                      </button>
                    )}
                  </>
                )}
              </div>
            ))}
            {isAddingTask ? (
              <div className="task-manager-item">
                <input
                  type="text"
                  value={newTaskName}
                  onChange={(e) => setNewTaskName(e.target.value)}
                  onBlur={handleAddTask}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleAddTask()
                    } else if (e.key === 'Escape') {
                      setIsAddingTask(false)
                      setNewTaskName('')
                    }
                  }}
                  placeholder="New task name..."
                  className="task-name-input"
                  autoFocus
                />
              </div>
            ) : (
              <button
                onClick={() => setIsAddingTask(true)}
                className="add-task-btn"
              >
                + Add Task
              </button>
            )}
          </div>
        </div>
      )}

      <div className="prompts-header">
        <button onClick={onAddPrompt} className="add-btn">+ Add Prompt</button>
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
