import { Prompt, BestPrompts } from '../types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'

interface OutputsSidebarProps {
  prompts: Prompt[]
  selectedTask: string
  onSavePrompt: (index: number) => void
  onSaveAll: () => void
  onRunAll: () => void
  onRunBest: () => void
  bestPrompts: BestPrompts
  loading: boolean
  tasks: string[]
}

export default function OutputsSidebar({
  prompts,
  selectedTask,
  onSavePrompt,
  onSaveAll,
  onRunAll,
  onRunBest,
  bestPrompts,
  loading,
  tasks
}: OutputsSidebarProps) {
  return (
    <div className="w-[350px] flex flex-col border-l-2 border-border pl-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold m-0">Outputs - {selectedTask}</h3>
      </div>
      <div className="flex-1 overflow-y-auto flex flex-col gap-4 mb-4">
        {prompts.length === 0 ? (
          <div className="text-center text-muted-foreground p-8 italic">No prompts added yet</div>
        ) : (
          prompts.map((prompt, index) => (
            <Card key={prompt.id}>
              <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                  <strong className="text-primary text-sm">{prompt.name}</strong>
                  {prompt.loading && <span className="text-base">⏳</span>}
                  {prompt.output && !prompt.loading && (
                    <Button
                      onClick={() => onSavePrompt(index)}
                      size="sm"
                      variant="secondary"
                    >
                      Save
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {prompt.output ? (
                  <pre className="text-xs max-h-[200px] overflow-y-auto bg-background/50 p-3 rounded whitespace-pre-wrap break-words leading-tight">
                    {prompt.output}
                  </pre>
                ) : (
                  <div className="text-muted-foreground italic text-sm">No output yet</div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
      <Button
        onClick={onRunAll}
        disabled={loading || prompts.length === 0}
        className="w-full mb-2 bg-cyan-600 hover:bg-cyan-700"
      >
        {loading ? 'Running All...' : 'Run All Prompts'}
      </Button>
      <Button
        onClick={onRunBest}
        disabled={loading || Object.keys(bestPrompts).length !== tasks.length}
        className="w-full font-semibold bg-green-600 hover:bg-green-700"
        title={Object.keys(bestPrompts).length !== tasks.length ? 'Select best prompt for all tasks first' : ''}
      >
        {loading ? 'Running Best...' : 'Run Best Prompts'}
      </Button>
    </div>
  )
}
