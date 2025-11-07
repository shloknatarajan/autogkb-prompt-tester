import { useState } from 'react'
import { Prompt, BestPrompts } from '../types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'

interface PromptsSidebarProps {
  prompts: Prompt[]
  tasks: string[]
  selectedTask: string
  selectedPromptIndex: number | null
  onSelectPrompt: (index: number) => void
  onAddPrompt: () => void
  onUpdatePrompt: (index: number, field: keyof Prompt, value: string) => void
  onDeletePrompt: (index: number) => void
  onSelectTask: (task: string) => void
  onAddTask: (taskName: string) => void
  onDeleteTask: (taskName: string) => void
  onRenameTask: (oldName: string, newName: string) => void
  bestPrompts: BestPrompts
  onSetBestPrompt: (task: string, promptId: number) => void
  loading?: boolean
  onSaveAll: () => void
}

export default function PromptsSidebar({
  prompts,
  tasks,
  selectedTask,
  selectedPromptIndex,
  onSelectPrompt,
  onAddPrompt,
  onUpdatePrompt,
  onDeletePrompt,
  onSelectTask,
  onAddTask,
  onDeleteTask,
  onRenameTask,
  bestPrompts,
  onSetBestPrompt,
  onSaveAll
}: PromptsSidebarProps) {
  const [showTaskManager, setShowTaskManager] = useState(false)
  const [isAddingTask, setIsAddingTask] = useState(false)
  const [newTaskName, setNewTaskName] = useState('')
  const [editingTask, setEditingTask] = useState<string | null>(null)
  const [editedName, setEditedName] = useState('')

  const handleAddTask = () => {
    if (newTaskName.trim()) {
      onAddTask(newTaskName.trim())
      setNewTaskName('')
      setIsAddingTask(false)
    }
  }

  const handleRenameTask = (oldName: string) => {
    if (editedName.trim() && editedName !== oldName) {
      onRenameTask(oldName, editedName.trim())
    }
    setEditingTask(null)
    setEditedName('')
  }

  const startEditing = (task: string) => {
    if (task !== 'Default') {
      setEditingTask(task)
      setEditedName(task)
    }
  }

  return (
    <div className="w-[250px] flex flex-col border-r-2 border-border pr-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold m-0">Prompts</h3>
      </div>

      <div className="flex gap-2 mb-4">
        <Select value={selectedTask} onValueChange={onSelectTask}>
          <SelectTrigger className="flex-1">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {tasks.map(task => (
              <SelectItem key={task} value={task}>{task}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          onClick={() => setShowTaskManager(!showTaskManager)}
          variant="outline"
          size="sm"
          className="px-3 text-lg"
          title="Manage tasks"
        >
          ⋯
        </Button>
      </div>

      {showTaskManager && (
        <Card className="mb-4">
          <CardContent className="pt-3">
            <div className="flex justify-between items-center mb-3">
              <strong className="text-sm">Manage Tasks</strong>
              <Button
                onClick={() => setShowTaskManager(false)}
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground text-xl"
              >
                ×
              </Button>
            </div>
            <div className="flex flex-col gap-2">
            {tasks.map((task) => (
              <div key={task} className="flex justify-between items-center p-2 bg-muted rounded gap-2">
                {editingTask === task ? (
                  <Input
                    type="text"
                    value={editedName}
                    onChange={(e) => setEditedName(e.target.value)}
                    onBlur={() => handleRenameTask(task)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleRenameTask(task)
                      }
                    }}
                    className="flex-1 h-7 text-sm"
                    autoFocus
                  />
                ) : (
                  <>
                    <span
                      className="flex-1 cursor-pointer text-sm"
                      onDoubleClick={() => startEditing(task)}
                    >
                      {task}
                    </span>
                    {task !== 'Default' && (
                      <Button
                        onClick={() => {
                          if (confirm(`Delete task "${task}" and all its prompts?`)) {
                            onDeleteTask(task)
                          }
                        }}
                        variant="destructive"
                        size="sm"
                        className="h-6 w-6 p-0 text-lg"
                      >
                        ×
                      </Button>
                    )}
                  </>
                )}
              </div>
            ))}
            {isAddingTask ? (
              <div className="flex justify-between items-center p-2 bg-muted rounded gap-2">
                <Input
                  type="text"
                  value={newTaskName}
                  onChange={(e) => setNewTaskName(e.target.value)}
                  onBlur={handleAddTask}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleAddTask()
                    } else if (e.key === 'Escape') {
                      setIsAddingTask(false)
                      setNewTaskName('')
                    }
                  }}
                  placeholder="New task name..."
                  className="flex-1 h-7 text-sm"
                  autoFocus
                />
              </div>
            ) : (
              <Button
                onClick={() => setIsAddingTask(true)}
                className="w-full bg-green-600 hover:bg-green-700 text-sm"
                size="sm"
              >
                + Add Task
              </Button>
            )}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="mb-2">
        <Button onClick={onAddPrompt} className="w-full bg-green-600 hover:bg-green-700" size="sm">
          + Add Prompt
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto flex flex-col gap-2 mb-4">
        {prompts.map((prompt, index) => {
          const isBest = bestPrompts[selectedTask] === prompt.id
          return (
            <Card
              key={prompt.id}
              className={`cursor-pointer transition-all border ${
                selectedPromptIndex === index
                  ? 'bg-primary/20 border-primary'
                  : 'hover:bg-muted/50'
              }`}
              onClick={() => onSelectPrompt(index)}
            >
              <CardContent className="p-3">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-lg cursor-pointer select-none transition-opacity ${
                      isBest ? 'opacity-100' : 'opacity-30 hover:opacity-60'
                    }`}
                    onClick={(e) => {
                      e.stopPropagation()
                      onSetBestPrompt(selectedTask, prompt.id)
                    }}
                    title={isBest ? 'Best prompt for this task' : 'Set as best prompt'}
                  >
                    ⭐
                  </span>
                  <Input
                    type="text"
                    value={prompt.name}
                    onChange={(e) => {
                      e.stopPropagation()
                      onUpdatePrompt(index, 'name', e.target.value)
                    }}
                    onClick={(e) => e.stopPropagation()}
                    className="flex-1 h-7 text-sm bg-transparent border-none hover:bg-muted/50 focus:bg-muted/50"
                  />
                  <Button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeletePrompt(index)
                    }}
                    variant="destructive"
                    size="sm"
                    className="h-6 w-6 p-0 text-lg"
                  >
                    ×
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
      <Button
        onClick={onSaveAll}
        disabled={prompts.length === 0}
        className="w-full bg-yellow-500 hover:bg-yellow-600 text-black font-semibold"
      >
        Save All Prompts
      </Button>
    </div>
  )
}
