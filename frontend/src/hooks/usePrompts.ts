import { useState, useEffect } from 'react';
import { Prompt, BestPrompts } from '../types';

const DEFAULT_CITATION_PROMPT = `You are analyzing a genetic variant annotation. Your task is to find direct quotes from the article text that support this specific annotation.

Annotation Details:
- Variant/Haplotype: {variant}
- Gene: {gene}
- Drug(s): {drug}
- Finding: {sentence}
- Notes: {notes}

Article Text:
{full_text}

Please identify 1-3 direct quotes from the article that provide evidence for this annotation. Focus on quotes that mention:
1. The specific variant or haplotype
2. The phenotype, outcome, or drug response
3. Statistical significance or effect size
4. Study population or methodology

Return your response as a JSON object with a "citations" array containing the exact quoted text:
{{
  "citations": [
    "Direct quote from article supporting this finding",
    "Another relevant quote if available"
  ]
}}

Important:
- Only include quotes that directly support THIS specific annotation
- Use exact quotes from the article text
- Do not fabricate or modify quotes
- Return empty array if no supporting quotes found`;

export function usePrompts() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [tasks, setTasks] = useState<string[]>(['Default']);
  const [selectedTask, setSelectedTask] = useState<string>('Default');
  const [selectedPromptIndex, setSelectedPromptIndex] = useState<number | null>(
    null,
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [bestPrompts, setBestPrompts] = useState<BestPrompts>({});

  // Filter prompts by selected task
  const filteredPrompts = prompts.filter((p) => p.task === selectedTask);

  // Load prompts from backend on initialization
  useEffect(() => {
    const loadPromptsAndBest = async () => {
      try {
        const response = await fetch('http://localhost:8000/prompts');
        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }
        const data = await response.json();

        // Transform backend prompts to frontend format
        const transformedPrompts: Prompt[] = data.prompts.map(
          (savedPrompt: any, index: number) => ({
            id: Date.now() + index,
            task: savedPrompt.task || 'Default',
            name: savedPrompt.name || `Prompt ${index + 1}`,
            prompt: savedPrompt.prompt || '',
            model: savedPrompt.model || 'openai/gpt-4o-mini',
            responseFormat: savedPrompt.response_format
              ? JSON.stringify(savedPrompt.response_format, null, 2)
              : '',
            output: savedPrompt.output
              ? typeof savedPrompt.output === 'string'
                ? savedPrompt.output
                : JSON.stringify(savedPrompt.output, null, 2)
              : null,
            loading: false,
          }),
        );

        // Extract unique tasks
        const uniqueTasks = [...new Set(transformedPrompts.map((p) => p.task))];
        if (uniqueTasks.length > 0) {
          setTasks(uniqueTasks);
          setSelectedTask(uniqueTasks[0]);
        }

        setPrompts(transformedPrompts);

        // After prompts are loaded, load best prompts configuration
        try {
          const bestResponse = await fetch(
            'http://localhost:8000/best-prompts',
          );
          if (bestResponse.ok) {
            const bestConfig = await bestResponse.json();
            console.log('Loaded best prompts config:', bestConfig);

            // Convert prompt names to IDs
            // bestConfig format: { "var-pheno": "structured", "var-drug": "from docs", ... }
            const bestPromptsById: BestPrompts = {};

            for (const [task, promptName] of Object.entries(bestConfig)) {
              const prompt = transformedPrompts.find(
                (p) => p.task === task && p.name === promptName,
              );
              if (prompt) {
                bestPromptsById[task] = prompt.id;
                console.log(
                  `Matched best prompt for ${task}: "${promptName}" (ID: ${prompt.id})`,
                );
              } else {
                console.warn(
                  `Best prompt not found for task "${task}" with name "${promptName}"`,
                );
              }
            }

            setBestPrompts(bestPromptsById);
            console.log('Applied best prompts:', bestPromptsById);
          }
        } catch (err) {
          console.warn('Failed to load best prompts config:', err);
          // Non-fatal error, continue without pre-selected best prompts
        }
      } catch (err) {
        console.error('Failed to load prompts:', err);
        setError('Failed to load saved prompts: ' + (err as Error).message);
      }
    };

    loadPromptsAndBest();
  }, []);

  const addNewPrompt = () => {
    const taskPrompts = prompts.filter((p) => p.task === selectedTask);
    const newPrompt: Prompt = {
      id: Date.now(),
      task: selectedTask,
      name: `Prompt ${taskPrompts.length + 1}`,
      prompt: '',
      model: 'openai/gpt-4o-mini',
      responseFormat: '',
      output: null,
      loading: false,
    };
    setPrompts([...prompts, newPrompt]);
    setSelectedPromptIndex(filteredPrompts.length);
  };

  const updatePrompt = (index: number, field: keyof Prompt, value: any) => {
    setPrompts(currentPrompts => {
      const updated = [...currentPrompts];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const deletePrompt = (index: number) => {
    const updated = prompts.filter((_, i) => i !== index);
    setPrompts(updated);
    if (selectedPromptIndex === index) {
      setSelectedPromptIndex(null);
    } else if (selectedPromptIndex !== null && selectedPromptIndex > index) {
      setSelectedPromptIndex(selectedPromptIndex - 1);
    }
  };

  const runPrompt = async (
    index: number,
    text: string,
    model: string = 'openai/gpt-4o-mini',
  ) => {
    const prompt = prompts[index];
    updatePrompt(index, 'loading', true);
    setError('');

    try {
      let parsedResponseFormat = null;
      if (prompt.responseFormat?.trim()) {
        try {
          parsedResponseFormat = JSON.parse(prompt.responseFormat);
        } catch (err) {
          setError(
            'Invalid JSON in response format: ' + (err as Error).message,
          );
          updatePrompt(index, 'loading', false);
          return;
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
          model: model,
          response_format: parsedResponseFormat,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      updatePrompt(index, 'output', data.output);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      updatePrompt(index, 'loading', false);
    }
  };

  const runAllPrompts = async (text: string, model: string = 'openai/gpt-4o-mini') => {
    setLoading(true);
    // Only run prompts for the selected task
    const taskPromptIndices = prompts
      .map((p, i) => ({ prompt: p, index: i }))
      .filter(({ prompt }) => prompt.task === selectedTask)
      .map(({ index }) => index);

    for (const index of taskPromptIndices) {
      await runPrompt(index, text, model);
    }
    setLoading(false);
  };

  const savePrompt = async (index: number, text: string) => {
    const prompt = prompts[index];
    try {
      const response = await fetch('http://localhost:8000/save-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task: prompt.task,
          name: prompt.name,
          prompt: prompt.prompt,
          text,
          model: prompt.model,
          response_format: prompt.responseFormat
            ? JSON.parse(prompt.responseFormat)
            : null,
          output: prompt.output,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      alert(data.message);
    } catch (err) {
      alert('Failed to save: ' + (err as Error).message);
    }
  };

  const saveAllPrompts = async (text: string) => {
    try {
      const response = await fetch('http://localhost:8000/save-all-prompts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompts: prompts,
          text,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      alert(data.message);
    } catch (err) {
      alert('Failed to save all prompts: ' + (err as Error).message);
    }
  };

  const addTask = (taskName: string) => {
    if (!tasks.includes(taskName)) {
      setTasks([...tasks, taskName]);
      setSelectedTask(taskName);
    }
  };

  const deleteTask = (taskName: string) => {
    if (taskName === 'Default') {
      alert('Cannot delete the Default task');
      return;
    }

    // Remove all prompts in this task
    const updated = prompts.filter((p) => p.task !== taskName);
    setPrompts(updated);

    // Remove task from list
    const updatedTasks = tasks.filter((t) => t !== taskName);
    setTasks(updatedTasks);

    // Select another task
    if (selectedTask === taskName) {
      setSelectedTask(updatedTasks[0] || 'Default');
    }
  };

  const renameTask = (oldName: string, newName: string) => {
    if (oldName === 'Default') {
      alert('Cannot rename the Default task');
      return;
    }

    if (tasks.includes(newName)) {
      alert('Task name already exists');
      return;
    }

    // Update all prompts with the old task name
    const updated = prompts.map((p) =>
      p.task === oldName ? { ...p, task: newName } : p,
    );
    setPrompts(updated);

    // Update tasks list
    const updatedTasks = tasks.map((t) => (t === oldName ? newName : t));
    setTasks(updatedTasks);

    // Update selected task if needed
    if (selectedTask === oldName) {
      setSelectedTask(newName);
    }

    // Update best prompts mapping
    if (bestPrompts[oldName]) {
      const updatedBest = { ...bestPrompts };
      updatedBest[newName] = updatedBest[oldName];
      delete updatedBest[oldName];
      setBestPrompts(updatedBest);
    }
  };

  const setBestPrompt = async (task: string, promptId: number) => {
    // Update local state
    const updatedBest = {
      ...bestPrompts,
      [task]: promptId,
    };
    setBestPrompts(updatedBest);

    try {
      // Build best prompts config for backend (task -> name mapping)
      const bestPromptsConfig: { [task: string]: string } = {};

      for (const [taskName, pId] of Object.entries(updatedBest)) {
        const prompt = prompts.find((p) => p.id === pId);
        if (prompt) {
          bestPromptsConfig[taskName] = prompt.name;
        }
      }

      // Persist to backend
      const response = await fetch('http://localhost:8000/best-prompts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          best_prompts: bestPromptsConfig,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      console.log('Best prompts updated successfully');
    } catch (err) {
      console.error('Failed to save best prompts:', err);
      // Don't show alert to user - this is a background save
    }
  };

  const runBestPrompts = async (
    text: string,
    model: string = 'openai/gpt-4o-mini',
  ) => {
    setLoading(true);
    setError('');

    try {
      // Collect best prompts for all tasks
      const bestPromptsData: any[] = [];

      for (const task of tasks) {
        const bestPromptId = bestPrompts[task];
        if (!bestPromptId) {
          setError(`No best prompt selected for task: ${task}`);
          setLoading(false);
          return;
        }

        const prompt = prompts.find((p) => p.id === bestPromptId);
        if (!prompt) {
          setError(`Best prompt not found for task: ${task}`);
          setLoading(false);
          return;
        }

        // Parse response format if needed
        let parsedResponseFormat = null;
        if (prompt.responseFormat?.trim()) {
          try {
            parsedResponseFormat = JSON.parse(prompt.responseFormat);
          } catch (err) {
            setError(
              `Invalid JSON in response format for ${task}: ${(err as Error).message}`,
            );
            setLoading(false);
            return;
          }
        }

        bestPromptsData.push({
          task: prompt.task,
          prompt: prompt.prompt,
          model: model,
          response_format: parsedResponseFormat,
          name: prompt.name,
        });
      }

      // Call backend
      const response = await fetch('http://localhost:8000/run-best-prompts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          best_prompts: bestPromptsData,
          citation_prompt: DEFAULT_CITATION_PROMPT,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();

      // Update outputs for best prompts
      const updatedPrompts = [...prompts];
      for (const task of tasks) {
        const bestPromptId = bestPrompts[task];
        const promptIndex = prompts.findIndex((p) => p.id === bestPromptId);
        if (promptIndex !== -1 && data.results[task]) {
          updatedPrompts[promptIndex].output =
            typeof data.results[task] === 'string'
              ? data.results[task]
              : JSON.stringify(data.results[task], null, 2);
        }
      }
      setPrompts(updatedPrompts);

      // Show citation stats in success message if citations were generated
      if (data.citations_generated > 0) {
        alert(
          `Success! Output saved to ${data.output_file}\n\n` +
            `Generated citations for ${data.citations_generated} annotation(s).\n\n`,
        );
      } else {
        alert(`Success! Output saved to ${data.output_file}`);
      }
    } catch (err) {
      setError((err as Error).message);
      alert('Failed to run best prompts: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return {
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
    runBestPrompts,
  };
}
