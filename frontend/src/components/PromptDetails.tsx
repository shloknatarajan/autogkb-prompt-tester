import { Prompt } from '../types'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'

interface PromptDetailsProps {
  prompt: Prompt
  onUpdate: (field: keyof Prompt, value: string) => void
  onRun: () => void
}

export default function PromptDetails({ prompt, onUpdate, onRun }: PromptDetailsProps) {
  return (
    <div className="p-4 bg-card rounded-lg border">
      <h3 className="text-lg font-semibold mb-4">Configure Prompt</h3>

      <div className="flex flex-col gap-2 mb-4">
        <Label htmlFor="response-format">Response Format (JSON Schema):</Label>
        <Textarea
          id="response-format"
          value={prompt.responseFormat}
          onChange={(e) => onUpdate('responseFormat', e.target.value)}
          placeholder='Optional: Enter JSON response format'
          rows={3}
          className="min-h-[100px]"
        />
      </div>

      <div className="flex flex-col gap-2 mb-4">
        <Label htmlFor="prompt">Prompt:</Label>
        <Textarea
          id="prompt"
          value={prompt.prompt}
          onChange={(e) => onUpdate('prompt', e.target.value)}
          placeholder="Enter your prompt here..."
          rows={4}
          className="min-h-[120px]"
        />
      </div>

      <Button
        onClick={onRun}
        disabled={prompt.loading}
        className="w-full"
      >
        {prompt.loading ? 'Running...' : 'Run This Prompt'}
      </Button>
    </div>
  )
}
