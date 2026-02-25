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

export interface BenchmarkFieldScore {
  mean: number
  scores: number[]
}

export interface DetailedSampleResult {
  sample_id: number
  field_scores: { [field: string]: number }
  field_values: {
    [field: string]: {
      ground_truth: any
      prediction: any
    }
  }
  dependency_issues?: string[]
}

export interface UnmatchedSample {
  [field: string]: any
}

export interface BenchmarkTaskResult {
  overall_score: number
  raw_score?: number
  field_scores?: {
    [field: string]: BenchmarkFieldScore
  }
  total_samples: number
  error?: string
  detailed_results?: DetailedSampleResult[]
  unmatched_ground_truth?: UnmatchedSample[]
  unmatched_predictions?: UnmatchedSample[]
}

export interface BenchmarkResult {
  timestamp: string
  pmcid: string
  prompts_used: {
    [task: string]: string
  }
  results: {
    [task: string]: BenchmarkTaskResult
  }
  metadata: {
    ground_truth_file: string
    total_tasks: number
    average_score: number
    tasks_with_errors: number
  }
}

export interface BenchmarkResultListItem {
  filename: string
  timestamp: string
  pmcid: string
  average_score: number
  total_tasks: number
  prompts_used: {
    [task: string]: string
  }
}
