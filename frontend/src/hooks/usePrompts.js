import { useState } from 'react'

export function usePrompts() {
  const [prompts, setPrompts] = useState([])
  const [selectedPromptIndex, setSelectedPromptIndex] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const addNewPrompt = () => {
    const newPrompt = {
      id: Date.now(),
      name: `Prompt ${prompts.length + 1}`,
      prompt: '',
      model: 'gpt-4o-mini',
      responseFormat: '',
      output: null,
      loading: false
    }
    setPrompts([...prompts, newPrompt])
    setSelectedPromptIndex(prompts.length)
  }

  const updatePrompt = (index, field, value) => {
    const updated = [...prompts]
    updated[index][field] = value
    setPrompts(updated)
  }

  const deletePrompt = (index) => {
    const updated = prompts.filter((_, i) => i !== index)
    setPrompts(updated)
    if (selectedPromptIndex === index) {
      setSelectedPromptIndex(null)
    } else if (selectedPromptIndex > index) {
      setSelectedPromptIndex(selectedPromptIndex - 1)
    }
  }

  const runPrompt = async (index, text) => {
    const prompt = prompts[index]
    updatePrompt(index, 'loading', true)
    setError('')

    try {
      let parsedResponseFormat = null
      if (prompt.responseFormat?.trim()) {
        try {
          parsedResponseFormat = JSON.parse(prompt.responseFormat)
        } catch (err) {
          setError('Invalid JSON in response format: ' + err.message)
          updatePrompt(index, 'loading', false)
          return
        }
      }

      const response = await fetch('http://localhost:8000/test-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.prompt,
          text,
          model: prompt.model,
          response_format: parsedResponseFormat
        })
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()
      updatePrompt(index, 'output', data.output)
    } catch (err) {
      setError(err.message)
    } finally {
      updatePrompt(index, 'loading', false)
    }
  }

  const runAllPrompts = async (text) => {
    setLoading(true)
    for (let i = 0; i < prompts.length; i++) {
      await runPrompt(i, text)
    }
    setLoading(false)
  }

  const savePrompt = async (index, text) => {
    const prompt = prompts[index]
    try {
      const response = await fetch('http://localhost:8000/save-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.prompt,
          text,
          model: prompt.model,
          response_format: prompt.responseFormat ? JSON.parse(prompt.responseFormat) : null,
          output: prompt.output
        })
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()
      alert(data.message)
    } catch (err) {
      alert('Failed to save: ' + err.message)
    }
  }

  const saveAllPrompts = async (text) => {
    try {
      const response = await fetch('http://localhost:8000/save-all-prompts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompts: prompts,
          text
        })
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()
      alert(data.message)
    } catch (err) {
      alert('Failed to save all prompts: ' + err.message)
    }
  }

  return {
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
  }
}
