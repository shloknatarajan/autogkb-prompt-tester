import { useState, useEffect, useCallback } from 'react';

const API_BASE = 'http://localhost:8000';

export interface PipelineJob {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  current_stage: string;
  progress: number;
  pmcids_processed: number;
  pmcids_total: number;
  current_pmcid: string | null;
  messages: string[];
  result: {
    output_directory: string;
    combined_file: string;
    results_file: string;
    total_pmcids: number;
    overall_score: number;
    task_scores: { [task: string]: number };
  } | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface PipelineJobSummary {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  current_stage: string;
  progress: number;
  pmcids_processed: number;
  pmcids_total: number;
  created_at: string;
  updated_at: string;
}

export interface PipelineResultSummary {
  filename: string;
  timestamp: string;
  total_pmcids: number;
  overall_score: number;
  config: {
    data_dir: string;
    model: string;
    concurrency: number;
  };
}

export interface PipelineBenchmarkResult {
  timestamp: string;
  config: {
    data_dir: string;
    model: string;
    concurrency: number;
  };
  output_directory: string;
  combined_file: string;
  summary: {
    total_pmcids: number;
    benchmarked_pmcids: number;
    scores: { [task: string]: number };
    overall: number;
    timestamp: string;
  };
  pmcid_results: {
    [pmcid: string]: {
      [task: string]: number | object | null;
    } | null;
  };
}

export function usePipeline() {
  const [jobs, setJobs] = useState<PipelineJobSummary[]>([]);
  const [currentJob, setCurrentJob] = useState<PipelineJob | null>(null);
  const [pipelineResults, setPipelineResults] = useState<PipelineResultSummary[]>([]);
  const [selectedPipelineResult, setSelectedPipelineResult] = useState<PipelineBenchmarkResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [eventSource, setEventSource] = useState<EventSource | null>(null);

  // Load all jobs and results on mount
  useEffect(() => {
    loadJobs();
    loadPipelineResults();
  }, []);

  // Cleanup event source on unmount
  useEffect(() => {
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [eventSource]);

  const loadJobs = async () => {
    try {
      const response = await fetch(`${API_BASE}/pipeline/jobs`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setJobs(data.jobs);
    } catch (err) {
      console.error('Failed to load pipeline jobs:', err);
    }
  };

  const startPipeline = async (
    dataDir: string = 'data/markdown',
    model: string = 'gpt-4o-mini',
    concurrency: number = 3,
  ) => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(`${API_BASE}/pipeline/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data_dir: dataDir,
          model: model,
          concurrency: concurrency,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || response.statusText);
      }

      const data = await response.json();
      const jobId = data.job_id;

      // Subscribe to SSE for this job
      subscribeToJob(jobId);

      // Reload jobs list
      await loadJobs();

      return jobId;
    } catch (err) {
      const errorMessage = (err as Error).message;
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const subscribeToJob = useCallback((jobId: string) => {
    // Close existing event source if any
    if (eventSource) {
      eventSource.close();
    }

    const es = new EventSource(`${API_BASE}/pipeline/events/${jobId}`);

    es.onmessage = (event) => {
      try {
        const jobData = JSON.parse(event.data) as PipelineJob;
        setCurrentJob(jobData);

        // Update jobs list with new status
        setJobs((prev) =>
          prev.map((job) =>
            job.id === jobId
              ? {
                  ...job,
                  status: jobData.status,
                  current_stage: jobData.current_stage,
                  progress: jobData.progress,
                  pmcids_processed: jobData.pmcids_processed,
                  pmcids_total: jobData.pmcids_total,
                  updated_at: jobData.updated_at,
                }
              : job,
          ),
        );

        // Close connection if job is done
        if (jobData.status === 'completed' || jobData.status === 'failed' || jobData.status === 'cancelled') {
          es.close();
          setEventSource(null);
          // Reload jobs to get final state
          loadJobs();
        }
      } catch (err) {
        console.error('Failed to parse SSE data:', err);
      }
    };

    es.onerror = () => {
      console.error('SSE connection error');
      es.close();
      setEventSource(null);
    };

    setEventSource(es);
  }, [eventSource]);

  const getJobStatus = async (jobId: string) => {
    try {
      const response = await fetch(`${API_BASE}/pipeline/status/${jobId}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setCurrentJob(data);
      return data;
    } catch (err) {
      console.error('Failed to get job status:', err);
      throw err;
    }
  };

  const selectJob = async (jobId: string) => {
    await getJobStatus(jobId);

    // If job is still running, subscribe to updates
    if (currentJob && (currentJob.status === 'pending' || currentJob.status === 'running')) {
      subscribeToJob(jobId);
    }
  };

  const clearCurrentJob = () => {
    if (eventSource) {
      eventSource.close();
      setEventSource(null);
    }
    setCurrentJob(null);
  };

  const loadPipelineResults = async () => {
    try {
      const response = await fetch(`${API_BASE}/pipeline/results`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setPipelineResults(data.files);
    } catch (err) {
      console.error('Failed to load pipeline results:', err);
    }
  };

  const loadPipelineResultDetail = async (filename: string) => {
    try {
      const response = await fetch(`${API_BASE}/pipeline/results/${filename}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setSelectedPipelineResult(data);
      return data;
    } catch (err) {
      console.error('Failed to load pipeline result detail:', err);
      throw err;
    }
  };

  const cancelJob = async (jobId: string) => {
    try {
      const response = await fetch(`${API_BASE}/pipeline/cancel/${jobId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || response.statusText);
      }

      const data = await response.json();

      // Update current job status
      if (currentJob && currentJob.id === jobId) {
        setCurrentJob((prev) => (prev ? { ...prev, status: 'cancelled' } : null));
      }

      // Update jobs list
      setJobs((prev) =>
        prev.map((job) =>
          job.id === jobId ? { ...job, status: 'cancelled' } : job,
        ),
      );

      // Close event source
      if (eventSource) {
        eventSource.close();
        setEventSource(null);
      }

      return data;
    } catch (err) {
      console.error('Failed to cancel job:', err);
      throw err;
    }
  };

  return {
    jobs,
    currentJob,
    pipelineResults,
    selectedPipelineResult,
    loading,
    error,
    startPipeline,
    loadJobs,
    getJobStatus,
    selectJob,
    clearCurrentJob,
    subscribeToJob,
    loadPipelineResults,
    loadPipelineResultDetail,
    cancelJob,
  };
}
