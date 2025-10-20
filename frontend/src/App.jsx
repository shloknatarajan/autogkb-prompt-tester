import { useState } from 'react'
import './App.css'
import PromptsSidebar from './components/PromptsSidebar'
import OutputsSidebar from './components/OutputsSidebar'
import PromptDetails from './components/PromptDetails'
import { usePrompts } from './hooks/usePrompts'

const MODELS = [
  'gpt-4o',
  'gpt-4o-mini',
  'gpt-4-turbo',
  'gpt-4',
  'gpt-3.5-turbo',
  'gpt-5',
  'gpt-5-mini',
  'gpt-5-pro'
]

function App() {
  const [text, setText] = useState('')
  const [globalModel, setGlobalModel] = useState('gpt-5-mini')
  const [PMCID, setPMCID] = useState('')
  const [selectedFileName, setSelectedFileName] = useState('')
  const {
    prompts,
    filteredPrompts,
    tasks,
    selectedTask,
    selectedPromptIndex,
    loading,
    error,
    bestPrompts,
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
    renameTask,
    setBestPrompt,
    runBestPrompts
  } = usePrompts()

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setText(e.target.result)
        setSelectedFileName(file.name)
      }
      reader.readAsText(file)
    }
  }

  const clearFile = () => {
    setSelectedFileName('')
    // Reset the file input
    const fileInput = document.getElementById('file-input')
    if (fileInput) {
      fileInput.value = ''
    }
  }

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
          onSelectTask={setSelectedTask}
          onAddTask={addTask}
          onDeleteTask={deleteTask}
          onRenameTask={renameTask}
          bestPrompts={bestPrompts}
          onSetBestPrompt={setBestPrompt}
          loading={loading}
          onSaveAll={() => saveAllPrompts(text)}
        />

        <div className="main-content">
          <div className="text-section">
            <div className="form-group">
              <label htmlFor="model">Global Model:</label>
              <select
                id="model"
                value={globalModel}
                onChange={(e) => setGlobalModel(e.target.value)}
              >
                {MODELS.map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="pmcid">PMCID:</label>
              <input
                type="text"
                id="pmcid"
                value={PMCID}
                onChange={(e) => setPMCID(e.target.value)}
                placeholder="Enter PMCID..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="file-input">Load from File:</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="file-input"
                  accept=".md,.markdown"
                  onChange={handleFileSelect}
                  className="file-input"
                />
                {selectedFileName && (
                  <span className="file-indicator">
                    📄 {selectedFileName}
                    <button onClick={clearFile} className="clear-file-btn" type="button">
                      ×
                    </button>
                  </span>
                )}
              </div>
            </div>

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
                runPrompt(actualIndex, text, globalModel)
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
          onRunAll={() => runAllPrompts(text, globalModel)}
          onRunBest={() => runBestPrompts(text, PMCID, globalModel)}
          bestPrompts={bestPrompts}
          loading={loading}
          tasks={tasks}
        />
      </div>
    </div>
  )
}

export default App
