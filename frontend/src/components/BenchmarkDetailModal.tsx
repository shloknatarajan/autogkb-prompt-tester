import { BenchmarkTaskResult } from '../types';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface BenchmarkDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: string;
  result: BenchmarkTaskResult | null;
}

export default function BenchmarkDetailModal({
  isOpen,
  onClose,
  task,
  result,
}: BenchmarkDetailModalProps) {
  if (!result) return null;

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-100';
    if (score >= 0.6) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Detailed Scores: {task}</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Overall Score */}
          <div className="flex items-center justify-between p-4 bg-muted rounded">
            <div>
              <div className="text-sm text-muted-foreground">Overall Score</div>
              <div
                className={`text-3xl font-bold ${getScoreColor(result.overall_score)}`}
              >
                {(result.overall_score * 100).toFixed(1)}%
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">
                Total Samples
              </div>
              <div className="text-2xl font-semibold">
                {result.total_samples}
              </div>
            </div>
          </div>

          {/* Field Scores */}
          {result.field_scores && Object.keys(result.field_scores).length > 0 && (
            <div>
              <h4 className="text-md font-semibold mb-3">
                Field-by-Field Breakdown
              </h4>
              <div className="space-y-2">
                {Object.entries(result.field_scores).map(([field, scores]) => (
                  <div
                    key={field}
                    className="p-3 border rounded hover:bg-muted/50"
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-sm">{field}</span>
                      <div className="flex items-center gap-3">
                        <span
                          className={`text-sm px-2 py-1 rounded font-semibold ${getScoreBgColor(scores.mean)} ${getScoreColor(scores.mean)}`}
                        >
                          {(scores.mean * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    {scores.scores && scores.scores.length > 1 && (
                      <div className="mt-2 text-xs text-muted-foreground">
                        Individual scores:{' '}
                        {scores.scores.map((s) => (s * 100).toFixed(0)).join(', ')}
                        %
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Raw Score (for phenotype) */}
          {result.raw_score !== undefined && (
            <div className="p-3 bg-muted/50 rounded">
              <div className="text-sm text-muted-foreground">Raw Score</div>
              <div className="text-lg font-semibold">
                {result.raw_score.toFixed(1)}
              </div>
            </div>
          )}

          {/* Error Message */}
          {result.error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
              <strong>Error:</strong> {result.error}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
