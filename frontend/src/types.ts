export interface Prompt {
  id: number
  task: string
  name: string
  prompt: string
  model: string
  responseFormat: string
  output: string | null
  loading: boolean
}

export interface BestPrompts {
  [task: string]: number
}
