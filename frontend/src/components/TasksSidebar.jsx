import React, { useState } from 'react'

export default function TasksSidebar({
  tasks,
  selectedTask,
  onSelectTask,
  onAddTask,
  onDeleteTask,
  onRenameTask
}) {
  const [isAdding, setIsAdding] = useState(false)
  const [newTaskName, setNewTaskName] = useState('')
  const [editingTask, setEditingTask] = useState(null)
  const [editedName, setEditedName] = useState('')

  const handleAdd = () => {
    if (newTaskName.trim()) {
      onAddTask(newTaskName.trim())
      setNewTaskName('')
      setIsAdding(false)
    }
  }

  const handleRename = (oldName) => {
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
    <div className="tasks-sidebar">
      <div className="sidebar-header">
        <h3>Tasks</h3>
        <button onClick={() => setIsAdding(true)} className="add-btn">+ Add</button>
      </div>

      <div className="tasks-list">
        {tasks.map((task) => (
          <div
            key={task}
            className={`task-item ${selectedTask === task ? 'selected' : ''}`}
            onClick={() => onSelectTask(task)}
          >
            {editingTask === task ? (
              <input
                type="text"
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                onBlur={() => handleRename(task)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleRename(task)
                  }
                }}
                onClick={(e) => e.stopPropagation()}
                className="task-name-input"
                autoFocus
              />
            ) : (
              <div className="task-item-header">
                <span
                  className="task-name"
                  onDoubleClick={() => startEditing(task)}
                >
                  {task}
                </span>
                {task !== 'Default' && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteTask(task)
                    }}
                    className="delete-btn"
                  >
                    ×
                  </button>
                )}
              </div>
            )}
          </div>
        ))}

        {isAdding && (
          <div className="task-item new-task">
            <input
              type="text"
              value={newTaskName}
              onChange={(e) => setNewTaskName(e.target.value)}
              onBlur={handleAdd}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleAdd()
                } else if (e.key === 'Escape') {
                  setIsAdding(false)
                  setNewTaskName('')
                }
              }}
              placeholder="New task name..."
              className="task-name-input"
              autoFocus
            />
          </div>
        )}
      </div>
    </div>
  )
}
