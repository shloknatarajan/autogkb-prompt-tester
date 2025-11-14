import { BenchmarkResult } from '../types';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BarChart3 } from 'lucide-react';

interface BenchmarkResultsTableProps {
  result: BenchmarkResult;
  onViewDetails: (task: string) => void;
}

export default function BenchmarkResultsTable({
  result,
  onViewDetails,
}: BenchmarkResultsTableProps) {
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

  const tasks = Object.keys(result.results);

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Benchmark Results
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              PMCID: {result.pmcid} • {new Date(result.timestamp).toLocaleString()}
            </p>
          </div>
          <div className="text-right">
            <div className="text-xs text-muted-foreground">Average Score</div>
            <div
              className={`text-2xl font-bold ${getScoreColor(result.metadata.average_score)}`}
            >
              {(result.metadata.average_score * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-4 font-semibold">Task</th>
                <th className="text-left py-2 px-4 font-semibold">
                  Prompt Used
                </th>
                <th className="text-center py-2 px-4 font-semibold">
                  Overall Score
                </th>
                <th className="text-center py-2 px-4 font-semibold">Samples</th>
                <th className="text-center py-2 px-4 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => {
                const taskResult = result.results[task];
                const promptUsed = result.prompts_used[task];

                return (
                  <tr key={task} className="border-b hover:bg-muted/50">
                    <td className="py-3 px-4 font-medium">{task}</td>
                    <td className="py-3 px-4 text-sm text-muted-foreground">
                      {promptUsed}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {taskResult.error ? (
                        <span className="text-red-600 text-sm">Error</span>
                      ) : (
                        <span
                          className={`inline-block px-3 py-1 rounded font-semibold ${getScoreBgColor(taskResult.overall_score)} ${getScoreColor(taskResult.overall_score)}`}
                        >
                          {(taskResult.overall_score * 100).toFixed(1)}%
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center text-sm">
                      {taskResult.total_samples}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Button
                        onClick={() => onViewDetails(task)}
                        size="sm"
                        variant="outline"
                        disabled={!!taskResult.error}
                      >
                        Details
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {result.metadata.tasks_with_errors > 0 && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-yellow-800 text-sm">
            ⚠️ {result.metadata.tasks_with_errors} task(s) had errors during
            benchmarking
          </div>
        )}
      </CardContent>
    </Card>
  );
}
