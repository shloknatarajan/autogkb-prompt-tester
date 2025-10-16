import { useState } from 'react'
import './App.css'
import PromptsSidebar from './components/PromptsSidebar'
import OutputsSidebar from './components/OutputsSidebar'
import PromptDetails from './components/PromptDetails'
import { usePrompts } from './hooks/usePrompts'

function App() {
  const [text, setText] = useState('')
  const {
    prompts,
    filteredPrompts,
    tasks,
    selectedTask,
    selectedPromptIndex,
    loading,
    error,
    addNewPrompt,
    updatePrompt,
    deletePrompt,
    runPrompt,
    runAllPrompts,
    savePrompt,
    saveAllPrompts,
    setSelectedPromptIndex,
    setSelectedTask,
    addTask,
    deleteTask,
    renameTask
  } = usePrompts()

  return (
    <div className="app">
      <h1>Prompt Tester</h1>

      <div className="container">
        <PromptsSidebar
          prompts={filteredPrompts}
          tasks={tasks}
          selectedTask={selectedTask}
          selectedPromptIndex={selectedPromptIndex}
          onSelectPrompt={setSelectedPromptIndex}
          onAddPrompt={addNewPrompt}
          onUpdatePrompt={(index, field, value) => {
            // Find actual index in full prompts array
            const actualIndex = prompts.findIndex(p => p.id === filteredPrompts[index].id)
            updatePrompt(actualIndex, field, value)
          }}
          onDeletePrompt={(index) => {
            const actualIndex = prompts.findIndex(p => p.id === filteredPrompts[index].id)
            deletePrompt(actualIndex)
          }}
          onRunAll={() => runAllPrompts(text)}
          onSelectTask={setSelectedTask}
          onAddTask={addTask}
          onDeleteTask={deleteTask}
          onRenameTask={renameTask}
          loading={loading}
        />

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

          {selectedPromptIndex !== null && filteredPrompts[selectedPromptIndex] && (
            <PromptDetails
              prompt={filteredPrompts[selectedPromptIndex]}
              onUpdate={(field, value) => {
                const actualIndex = prompts.findIndex(p => p.id === filteredPrompts[selectedPromptIndex].id)
                updatePrompt(actualIndex, field, value)
              }}
              onRun={() => {
                const actualIndex = prompts.findIndex(p => p.id === filteredPrompts[selectedPromptIndex].id)
                runPrompt(actualIndex, text)
              }}
            />
          )}

          {error && (
            <div className="error">
              <h3>Error:</h3>
              <p>{error}</p>
            </div>
          )}
        </div>

        <OutputsSidebar
          prompts={filteredPrompts}
          selectedTask={selectedTask}
          onSavePrompt={(index) => {
            const actualIndex = prompts.findIndex(p => p.id === filteredPrompts[index].id)
            savePrompt(actualIndex, text)
          }}
          onSaveAll={() => saveAllPrompts(text)}
        />
      </div>
    </div>
  )
}

export default App
