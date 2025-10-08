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
    setSelectedPromptIndex
  } = usePrompts()

  return (
    <div className="app">
      <h1>Prompt Tester</h1>

      <div className="container">
        <PromptsSidebar
          prompts={prompts}
          selectedPromptIndex={selectedPromptIndex}
          onSelectPrompt={setSelectedPromptIndex}
          onAddPrompt={addNewPrompt}
          onUpdatePrompt={updatePrompt}
          onDeletePrompt={deletePrompt}
          onRunAll={() => runAllPrompts(text)}
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

          {selectedPromptIndex !== null && prompts[selectedPromptIndex] && (
            <PromptDetails
              prompt={prompts[selectedPromptIndex]}
              onUpdate={(field, value) => updatePrompt(selectedPromptIndex, field, value)}
              onRun={() => runPrompt(selectedPromptIndex, text)}
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
          prompts={prompts}
          onSavePrompt={(index) => savePrompt(index, text)}
          onSaveAll={() => saveAllPrompts(text)}
        />
      </div>
    </div>
  )
}

export default App
