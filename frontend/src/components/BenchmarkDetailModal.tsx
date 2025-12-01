import { BenchmarkTaskResult } from '../types';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';

interface BenchmarkDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: string;
  result: BenchmarkTaskResult | null;
  alignedVariants?: string[];
}

export default function BenchmarkDetailModal({
  isOpen,
  onClose,
  task,
  result,
  alignedVariants,
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

          {/* Aligned Variants (FA-specific) */}
          {alignedVariants && alignedVariants.length > 0 && (
            <div>
              <h4 className="text-md font-semibold mb-3">
                Aligned Variants
              </h4>
              <div className="flex flex-wrap gap-1">
                {alignedVariants.map((v, i) => (
                  <Badge key={i} variant="outline">
                    {v}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Per-Sample Comparison View */}
          {result.detailed_results && result.detailed_results.length > 0 && (
            <div>
              <h4 className="text-md font-semibold mb-3">
                Sample-by-Sample Comparison
              </h4>
              <div className="space-y-4">
                {result.detailed_results.map((sample) => (
                  <div key={sample.sample_id} className="border rounded-lg p-4">
                    <h5 className="font-semibold mb-3 flex items-center gap-2">
                      Sample {sample.sample_id}
                      <span className="text-xs font-normal text-muted-foreground">
                        ({Object.keys(sample.field_values).length} fields)
                      </span>
                    </h5>

                    <div className="space-y-2">
                      {Object.entries(sample.field_values)
                        .sort(([fieldA], [fieldB]) => {
                          const scoreA = sample.field_scores[fieldA] || 0;
                          const scoreB = sample.field_scores[fieldB] || 0;
                          return scoreA - scoreB;
                        })
                        .map(([field, values]) => {
                          const score = sample.field_scores[field] || 0;
                          const isMatch = score === 1.0;

                          return (
                            <div
                              key={field}
                              className={`p-2 rounded border ${
                                isMatch
                                  ? 'bg-green-50 border-green-200'
                                  : score >= 0.5
                                  ? 'bg-yellow-50 border-yellow-200'
                                  : 'bg-red-50 border-red-200'
                              }`}
                            >
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs font-medium text-muted-foreground">
                                  {field}
                                </span>
                                <span
                                  className={`text-xs px-2 py-0.5 rounded ${getScoreBgColor(score)} ${getScoreColor(score)}`}
                                >
                                  {(score * 100).toFixed(0)}%
                                </span>
                              </div>

                              <div className="grid grid-cols-2 gap-2 text-sm">
                                <div>
                                  <div className="text-xs text-muted-foreground mb-0.5">
                                    Ground Truth
                                  </div>
                                  <div className="font-mono text-xs break-words">
                                    {values.ground_truth !== null && values.ground_truth !== undefined
                                      ? String(values.ground_truth)
                                      : <span className="italic text-muted-foreground">null</span>}
                                  </div>
                                </div>
                                <div>
                                  <div className="text-xs text-muted-foreground mb-0.5">
                                    Prediction
                                  </div>
                                  <div className="font-mono text-xs break-words">
                                    {values.prediction !== null && values.prediction !== undefined
                                      ? String(values.prediction)
                                      : <span className="italic text-muted-foreground">null</span>}
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                    </div>

                    {/* Dependency Issues */}
                    {sample.dependency_issues && sample.dependency_issues.length > 0 && (
                      <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded">
                        <div className="text-xs font-medium text-orange-800 mb-1">
                          Dependency Issues:
                        </div>
                        <ul className="text-xs text-orange-700 list-disc list-inside">
                          {sample.dependency_issues.map((issue, i) => (
                            <li key={i}>{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Unmatched Ground Truth Samples */}
          {result.unmatched_ground_truth && result.unmatched_ground_truth.length > 0 && (
            <div>
              <h4 className="text-md font-semibold mb-3 flex items-center gap-2">
                <span className="text-orange-600">⚠️</span>
                Unmatched Ground Truth Samples
                <Badge variant="outline" className="bg-orange-50 text-orange-700">
                  {result.unmatched_ground_truth.length} missing
                </Badge>
              </h4>
              <p className="text-xs text-muted-foreground mb-3">
                These ground truth samples couldn't be matched with any predictions (LLM missed them)
              </p>

              <div className="space-y-2">
                {result.unmatched_ground_truth.map((sample, idx) => (
                  <div
                    key={idx}
                    className="p-3 border border-orange-200 rounded bg-orange-50"
                  >
                    <div className="text-xs font-medium text-orange-800 mb-2">
                      Missing Sample {idx + 1}
                    </div>

                    <div className="space-y-1">
                      {Object.entries(sample).map(([field, value]) => (
                        <div key={field} className="text-xs">
                          <span className="font-medium text-muted-foreground">{field}:</span>{' '}
                          <span className="font-mono">
                            {value !== null && value !== undefined
                              ? String(value)
                              : <span className="italic text-muted-foreground">null</span>}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Unmatched Prediction Samples (Extraneous) */}
          {result.unmatched_predictions && result.unmatched_predictions.length > 0 && (
            <div>
              <h4 className="text-md font-semibold mb-3 flex items-center gap-2">
                <span className="text-purple-600">➕</span>
                Unmatched Prediction Samples
                <Badge variant="outline" className="bg-purple-50 text-purple-700">
                  {result.unmatched_predictions.length} extra
                </Badge>
              </h4>
              <p className="text-xs text-muted-foreground mb-3">
                These predictions couldn't be matched with ground truth (LLM hallucinated or over-predicted)
              </p>

              <div className="space-y-2">
                {result.unmatched_predictions.map((sample, idx) => (
                  <div
                    key={idx}
                    className="p-3 border border-purple-200 rounded bg-purple-50"
                  >
                    <div className="text-xs font-medium text-purple-800 mb-2">
                      Extraneous Sample {idx + 1}
                    </div>

                    <div className="space-y-1">
                      {Object.entries(sample).map(([field, value]) => (
                        <div key={field} className="text-xs">
                          <span className="font-medium text-muted-foreground">{field}:</span>{' '}
                          <span className="font-mono">
                            {value !== null && value !== undefined
                              ? String(value)
                              : <span className="italic text-muted-foreground">null</span>}
                          </span>
                        </div>
                      ))}
                    </div>
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
