import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  AlertCircle,
  PlayCircle,
  CheckCircle,
  Loader2,
  Clock,
  Cpu,
  StopCircle,
  XCircle,
} from 'lucide-react';
import { PipelineJob, PipelineJobSummary } from '../hooks/usePipeline';

interface PipelineRunnerProps {
  currentJob: PipelineJob | null;
  jobs: PipelineJobSummary[];
  loading: boolean;
  error: string;
  onStartPipeline: (dataDir: string, model: string, concurrency: number) => Promise<string>;
  onSelectJob: (jobId: string) => Promise<void>;
  onCancelJob?: (jobId: string) => Promise<void>;
}

export default function PipelineRunner({
  currentJob,
  jobs,
  loading,
  error,
  onStartPipeline,
  onSelectJob,
  onCancelJob,
}: PipelineRunnerProps) {
  const [dataDir, setDataDir] = useState<string>('data/markdown');
  const [model, setModel] = useState<string>('gpt-4o-mini');
  const [concurrency, setConcurrency] = useState<number>(3);
  const [cancelling, setCancelling] = useState<boolean>(false);

  const handleStartPipeline = async () => {
    if (!dataDir.trim()) {
      alert('Please enter a data directory');
      return;
    }

    try {
      await onStartPipeline(dataDir, model, concurrency);
    } catch (err) {
      // Error handled by hook
    }
  };

  const getStageLabel = (stage: string): string => {
    const labels: { [key: string]: string } = {
      initializing: 'Initializing',
      loading_configuration: 'Loading Configuration',
      processing_pmcids: 'Processing PMCIDs',
      combining_outputs: 'Combining Outputs',
      running_benchmarks: 'Running Benchmarks',
      saving_results: 'Saving Results',
      completed: 'Completed',
    };
    return labels[stage] || stage;
  };

  const handleCancelPipeline = async () => {
    if (!currentJob || !onCancelJob) return;

    try {
      setCancelling(true);
      await onCancelJob(currentJob.id);
    } catch (err) {
      console.error('Failed to cancel pipeline:', err);
    } finally {
      setCancelling(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'running':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'cancelled':
        return <XCircle className="w-4 h-4 text-orange-500" />;
      default:
        return <Cpu className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Cpu className="w-5 h-5" />
            Full Benchmark Pipeline
          </h3>
          <p className="text-sm text-muted-foreground">
            Process all PMCIDs with best prompts and benchmark results
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Configuration */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Data Directory
              </label>
              <Input
                value={dataDir}
                onChange={(e) => setDataDir(e.target.value)}
                placeholder="data/markdown"
                disabled={loading || currentJob?.status === 'running'}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Model</label>
              <Select
                value={model}
                onValueChange={setModel}
                disabled={loading || currentJob?.status === 'running'}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4o-mini">GPT-4o Mini</SelectItem>
                  <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                  <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Concurrency</label>
              <Input
                type="number"
                min={1}
                max={10}
                value={concurrency}
                onChange={(e) => setConcurrency(parseInt(e.target.value) || 1)}
                disabled={loading || currentJob?.status === 'running'}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleStartPipeline}
              disabled={loading || currentJob?.status === 'running'}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Starting Pipeline...
                </>
              ) : currentJob?.status === 'running' ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Pipeline Running...
                </>
              ) : (
                <>
                  <PlayCircle className="w-4 h-4 mr-2" />
                  Start Full Pipeline
                </>
              )}
            </Button>

            {currentJob?.status === 'running' && onCancelJob && (
              <Button
                onClick={handleCancelPipeline}
                disabled={cancelling}
                variant="destructive"
                className="bg-red-600 hover:bg-red-700"
              >
                {cancelling ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Cancelling...
                  </>
                ) : (
                  <>
                    <StopCircle className="w-4 h-4 mr-2" />
                    Cancel
                  </>
                )}
              </Button>
            )}
          </div>

          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <div>{error}</div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Current Job Progress */}
      {currentJob && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold flex items-center gap-2">
              {getStatusIcon(currentJob.status)}
              Pipeline Progress
            </h3>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Progress bar */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>{getStageLabel(currentJob.current_stage)}</span>
                <span>{(currentJob.progress * 100).toFixed(0)}%</span>
              </div>
              <Progress value={currentJob.progress * 100} className="h-2" />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-muted p-3 rounded">
                <div className="text-2xl font-bold">
                  {currentJob.pmcids_processed}
                </div>
                <div className="text-xs text-muted-foreground">Processed</div>
              </div>
              <div className="bg-muted p-3 rounded">
                <div className="text-2xl font-bold">
                  {currentJob.pmcids_total}
                </div>
                <div className="text-xs text-muted-foreground">Total</div>
              </div>
              <div className="bg-muted p-3 rounded">
                <div className="text-2xl font-bold">
                  {currentJob.current_pmcid || '-'}
                </div>
                <div className="text-xs text-muted-foreground">Current</div>
              </div>
            </div>

            {/* Messages log */}
            <div>
              <label className="block text-sm font-medium mb-2">Log</label>
              <div className="bg-black text-green-400 p-3 rounded font-mono text-xs h-48 overflow-y-auto">
                {currentJob.messages.map((msg, i) => (
                  <div key={i}>{msg}</div>
                ))}
              </div>
            </div>

            {/* Results (if completed) */}
            {currentJob.status === 'completed' && currentJob.result && (
              <div className="bg-green-50 border border-green-200 rounded p-4">
                <h4 className="font-semibold text-green-800 mb-2">
                  Pipeline Completed Successfully!
                </h4>
                <div className="space-y-1 text-sm text-green-700">
                  <div>
                    <strong>Overall Score:</strong>{' '}
                    {(currentJob.result.overall_score * 100).toFixed(1)}%
                  </div>
                  <div>
                    <strong>Total PMCIDs:</strong>{' '}
                    {currentJob.result.total_pmcids}
                  </div>
                  <div>
                    <strong>Output Directory:</strong>{' '}
                    {currentJob.result.output_directory}
                  </div>
                  <div>
                    <strong>Results File:</strong>{' '}
                    {currentJob.result.results_file}
                  </div>
                  <div className="mt-2">
                    <strong>Task Scores:</strong>
                    <ul className="ml-4 mt-1">
                      {Object.entries(currentJob.result.task_scores).map(
                        ([task, score]) => (
                          <li key={task}>
                            {task}: {(score * 100).toFixed(1)}%
                          </li>
                        ),
                      )}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Error (if failed) */}
            {currentJob.status === 'failed' && currentJob.error && (
              <div className="bg-red-50 border border-red-200 rounded p-4">
                <h4 className="font-semibold text-red-800 mb-2">
                  Pipeline Failed
                </h4>
                <div className="text-sm text-red-700">{currentJob.error}</div>
              </div>
            )}

            {/* Cancelled */}
            {currentJob.status === 'cancelled' && (
              <div className="bg-orange-50 border border-orange-200 rounded p-4">
                <h4 className="font-semibold text-orange-800 mb-2">
                  Pipeline Cancelled
                </h4>
                <div className="text-sm text-orange-700">
                  Pipeline was cancelled by user. Processed {currentJob.pmcids_processed} of {currentJob.pmcids_total} PMCIDs.
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Previous Jobs */}
      {jobs.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold">Previous Pipeline Jobs</h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {jobs.slice(0, 10).map((job) => (
                <div
                  key={job.id}
                  className={`flex items-center justify-between p-3 border rounded cursor-pointer hover:bg-muted/50 ${
                    currentJob?.id === job.id ? 'bg-muted border-primary' : ''
                  }`}
                  onClick={() => onSelectJob(job.id)}
                >
                  <div className="flex items-center gap-2">
                    {getStatusIcon(job.status)}
                    <div>
                      <div className="font-medium text-sm">
                        {new Date(job.created_at).toLocaleString()}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {job.pmcids_processed}/{job.pmcids_total} PMCIDs •{' '}
                        {getStageLabel(job.current_stage)}
                      </div>
                    </div>
                  </div>
                  <div className="text-sm font-medium">
                    {(job.progress * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
