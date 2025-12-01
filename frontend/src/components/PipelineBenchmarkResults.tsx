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
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronUp, FileText, BarChart3 } from 'lucide-react';
import BenchmarkDetailModal from './BenchmarkDetailModal';
import { BenchmarkTaskResult, BenchmarkFieldScore } from '../types';

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

// Adapter function to convert DetailedResult to BenchmarkTaskResult
const convertToBenchmarkTaskResult = (
  result: DetailedResult
): { taskResult: BenchmarkTaskResult; alignedVariants?: string[] } => {
  const field_scores: { [field: string]: BenchmarkFieldScore } = {};

  for (const [field, data] of Object.entries(result.field_scores)) {
    field_scores[field] = {
      mean: data.mean_score,  // Rename mean_score → mean
      scores: data.scores
    };
  }

  return {
    taskResult: {
      overall_score: result.overall_score,
      total_samples: result.total_samples,
      field_scores: field_scores,
      error: result.status === 'error' ? result.status : undefined
    },
    alignedVariants: result.aligned_variants
  };
};

export default function PipelineBenchmarkResults({
  result,
}: PipelineBenchmarkResultsProps) {
  const [expandedPmcid, setExpandedPmcid] = useState<string | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedDetailTask, setSelectedDetailTask] = useState<string | null>(null);
  const [selectedDetailResult, setSelectedDetailResult] = useState<BenchmarkTaskResult | null>(null);
  const [selectedAlignedVariants, setSelectedAlignedVariants] = useState<string[] | undefined>(undefined);

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
    detailedResult: DetailedResult,
  ) => {
    const { taskResult, alignedVariants } = convertToBenchmarkTaskResult(detailedResult);
    setSelectedDetailTask(`${pmcid} - ${task}`);
    setSelectedDetailResult(taskResult);
    setSelectedAlignedVariants(alignedVariants);
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
                      const score = scores?.[task];

                      return (
                        <TableCell key={task}>
                          {score !== undefined && score !== null ? (
                            typeof score === 'object' ? (
                              <Button
                                variant="ghost"
                                size="sm"
                                className={`px-2 py-1 h-auto ${getScoreColor(getNumericScore(score))}`}
                                onClick={() => {
                                  handleViewDetails(
                                    pmcid,
                                    task,
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

      {/* Detail Modal - Reuse BenchmarkDetailModal */}
      <BenchmarkDetailModal
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        task={selectedDetailTask || ''}
        result={selectedDetailResult}
        alignedVariants={selectedAlignedVariants}
      />
    </div>
  );
}
