import { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronUp, FileText, BarChart3 } from 'lucide-react';

interface PipelineBenchmarkResult {
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
      [task: string]: number | DetailedResult | null;
    } | null;
  };
}

interface DetailedResult {
  total_samples: number;
  field_scores: { [field: string]: { mean_score: number; scores: number[] } };
  overall_score: number;
  detailed_results: Array<{
    sample_id: number;
    field_scores: { [field: string]: number };
    dependency_issues?: string[];
  }>;
  status?: string;
  aligned_variants?: string[];
}

interface PipelineBenchmarkResultsProps {
  result: PipelineBenchmarkResult;
}

export default function PipelineBenchmarkResults({
  result,
}: PipelineBenchmarkResultsProps) {
  const [expandedPmcid, setExpandedPmcid] = useState<string | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState<{
    pmcid: string;
    task: string;
    result: DetailedResult;
  } | null>(null);

  // Extract task names from summary scores
  const taskNames = Object.keys(result.summary.scores);

  // Format task names for display
  const formatTaskName = (task: string): string => {
    const names: { [key: string]: string } = {
      'var-pheno': 'Phenotype',
      'var-drug': 'Drug',
      'var-fa': 'FA',
      'study-parameters': 'Study Params',
    };
    return names[task] || task;
  };

  // Convert task name to annotation key used in pmcid_results
  const taskToAnnotationKey = (task: string): string => {
    const mapping: { [key: string]: string } = {
      'var-pheno': 'var_pheno_ann',
      'var-drug': 'var_drug_ann',
      'var-fa': 'var_fa_ann',
      'study-parameters': 'study_parameters',
    };
    return mapping[task] || task;
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.5) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const formatScore = (score: number | DetailedResult): string => {
    if (typeof score === 'number') {
      // Phenotype returns 0-100, others return 0-1
      if (score > 1) {
        return `${score.toFixed(1)}%`;
      }
      return `${(score * 100).toFixed(1)}%`;
    }
    return `${(score.overall_score * 100).toFixed(1)}%`;
  };

  const getNumericScore = (score: number | DetailedResult): number => {
    if (typeof score === 'number') {
      return score > 1 ? score / 100 : score;
    }
    return score.overall_score;
  };

  const handleViewDetails = (
    pmcid: string,
    task: string,
    result: DetailedResult,
  ) => {
    setSelectedDetail({ pmcid, task, result });
    setDetailModalOpen(true);
  };

  // Sort PMCIDs by number of tasks (descending) then by average score
  const sortedPmcids = Object.entries(result.pmcid_results)
    .filter(([, scores]) => scores !== null)
    .sort(([, a], [, b]) => {
      const aCount = Object.keys(a!).length;
      const bCount = Object.keys(b!).length;
      return bCount - aCount;
    });

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Pipeline Benchmark Summary
          </h3>
          <p className="text-sm text-muted-foreground">
            {new Date(result.timestamp).toLocaleString()}
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted p-4 rounded">
              <div className="text-2xl font-bold">
                {(result.summary.overall * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-muted-foreground">Overall Score</div>
            </div>
            <div className="bg-muted p-4 rounded">
              <div className="text-2xl font-bold">
                {result.summary.total_pmcids}
              </div>
              <div className="text-sm text-muted-foreground">Total PMCIDs</div>
            </div>
            <div className="bg-muted p-4 rounded">
              <div className="text-2xl font-bold">
                {result.summary.benchmarked_pmcids}
              </div>
              <div className="text-sm text-muted-foreground">Benchmarked</div>
            </div>
            <div className="bg-muted p-4 rounded">
              <div className="text-2xl font-bold">
                {result.config.concurrency}
              </div>
              <div className="text-sm text-muted-foreground">Concurrency</div>
            </div>
          </div>

          {/* Task Scores */}
          <div className="mb-4">
            <h4 className="font-medium mb-2">Average Task Scores</h4>
            <div className="flex flex-wrap gap-2">
              {Object.entries(result.summary.scores).map(([task, score]) => (
                <Badge
                  key={task}
                  className={`text-sm ${getScoreColor(score)} border-none`}
                >
                  {task}: {(score * 100).toFixed(1)}%
                </Badge>
              ))}
            </div>
          </div>

          {/* Config Info */}
          <div className="text-sm text-muted-foreground">
            <div>Model: {result.config.model}</div>
            <div>Data Dir: {result.config.data_dir}</div>
            <div>Output: {result.output_directory}</div>
          </div>
        </CardContent>
      </Card>

      {/* PMCID Results Table */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Per-PMCID Results
          </h3>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[150px]">PMCID</TableHead>
                {taskNames.map((task) => (
                  <TableHead key={task}>{formatTaskName(task)}</TableHead>
                ))}
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedPmcids.map(([pmcid, scores]) => (
                <>
                  <TableRow key={pmcid}>
                    <TableCell className="font-mono text-sm">{pmcid}</TableCell>
                    {taskNames.map((task) => {
                      const annotationKey = taskToAnnotationKey(task);
                      const score = scores?.[annotationKey];

                      return (
                        <TableCell key={task}>
                          {score !== undefined ? (
                            typeof score === 'object' ? (
                              <Button
                                variant="ghost"
                                size="sm"
                                className={`px-2 py-1 h-auto ${getScoreColor(getNumericScore(score))}`}
                                onClick={() => {
                                  handleViewDetails(
                                    pmcid,
                                    annotationKey,
                                    score as DetailedResult,
                                  );
                                }}
                              >
                                {formatScore(score)}
                              </Button>
                            ) : (
                              <span
                                className={`px-2 py-1 rounded ${getScoreColor(getNumericScore(score))}`}
                              >
                                {formatScore(score)}
                              </span>
                            )
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </TableCell>
                      );
                    })}
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setExpandedPmcid(
                            expandedPmcid === pmcid ? null : pmcid,
                          )
                        }
                      >
                        {expandedPmcid === pmcid ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </Button>
                    </TableCell>
                  </TableRow>
                  {expandedPmcid === pmcid && (
                    <TableRow>
                      <TableCell colSpan={taskNames.length + 2} className="bg-muted/50">
                        <div className="p-4 space-y-2">
                          <div className="font-medium">Task Details:</div>
                          {Object.entries(scores!).map(([task, result]) => (
                            <div key={task} className="ml-4">
                              <span className="font-mono text-sm">{task}:</span>{' '}
                              {typeof result === 'object' && result !== null ? (
                                <span className="text-sm">
                                  {(result as DetailedResult).total_samples}{' '}
                                  samples,{' '}
                                  {(
                                    (result as DetailedResult).overall_score *
                                    100
                                  ).toFixed(1)}
                                  % overall
                                  {(result as DetailedResult).status && (
                                    <span className="ml-2 text-muted-foreground">
                                      ({(result as DetailedResult).status})
                                    </span>
                                  )}
                                </span>
                              ) : (
                                <span className="text-sm">
                                  {formatScore(result as number)}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Detail Modal */}
      <Dialog open={detailModalOpen} onOpenChange={setDetailModalOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedDetail?.pmcid} - {selectedDetail?.task}
            </DialogTitle>
          </DialogHeader>
          {selectedDetail && (
            <div className="space-y-4">
              {/* Overall Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-muted p-3 rounded">
                  <div className="text-xl font-bold">
                    {(selectedDetail.result.overall_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Overall Score
                  </div>
                </div>
                <div className="bg-muted p-3 rounded">
                  <div className="text-xl font-bold">
                    {selectedDetail.result.total_samples}
                  </div>
                  <div className="text-xs text-muted-foreground">Samples</div>
                </div>
                <div className="bg-muted p-3 rounded">
                  <div className="text-xl font-bold">
                    {Object.keys(selectedDetail.result.field_scores).length}
                  </div>
                  <div className="text-xs text-muted-foreground">Fields</div>
                </div>
              </div>

              {/* Status */}
              {selectedDetail.result.status && (
                <div className="text-sm">
                  <span className="font-medium">Status: </span>
                  {selectedDetail.result.status}
                </div>
              )}

              {/* Field Scores */}
              <div>
                <h4 className="font-medium mb-2">Field Scores</h4>
                <div className="max-h-60 overflow-y-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Field</TableHead>
                        <TableHead>Mean Score</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {Object.entries(selectedDetail.result.field_scores)
                        .sort(([, a], [, b]) => b.mean_score - a.mean_score)
                        .map(([field, data]) => (
                          <TableRow key={field}>
                            <TableCell className="text-sm">{field}</TableCell>
                            <TableCell>
                              <span
                                className={`px-2 py-1 rounded ${getScoreColor(data.mean_score)}`}
                              >
                                {(data.mean_score * 100).toFixed(1)}%
                              </span>
                            </TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </div>
              </div>

              {/* Aligned Variants (for FA) */}
              {selectedDetail.result.aligned_variants &&
                selectedDetail.result.aligned_variants.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Aligned Variants</h4>
                    <div className="flex flex-wrap gap-1">
                      {selectedDetail.result.aligned_variants.map((v, i) => (
                        <Badge key={i} variant="outline">
                          {v}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

              {/* Per-Sample Details */}
              {selectedDetail.result.detailed_results.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Sample Details</h4>
                  <div className="max-h-60 overflow-y-auto">
                    {selectedDetail.result.detailed_results.map((sample) => (
                      <div
                        key={sample.sample_id}
                        className="border rounded p-3 mb-2"
                      >
                        <div className="font-medium text-sm mb-2">
                          Sample {sample.sample_id}
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                          {Object.entries(sample.field_scores)
                            .sort(([, a], [, b]) => b - a)
                            .slice(0, 12)
                            .map(([field, score]) => (
                              <div key={field} className="flex justify-between">
                                <span className="truncate mr-2">{field}:</span>
                                <span
                                  className={
                                    score === 1
                                      ? 'text-green-600'
                                      : score === 0
                                        ? 'text-red-600'
                                        : 'text-yellow-600'
                                  }
                                >
                                  {(score * 100).toFixed(0)}%
                                </span>
                              </div>
                            ))}
                        </div>
                        {sample.dependency_issues &&
                          sample.dependency_issues.length > 0 && (
                            <div className="mt-2 text-xs text-orange-600">
                              Issues: {sample.dependency_issues.join(', ')}
                            </div>
                          )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
