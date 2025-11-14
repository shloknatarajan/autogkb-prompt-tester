import { BenchmarkResultListItem } from '../types';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { History, ChevronRight } from 'lucide-react';

interface BenchmarkHistoryListProps {
  results: BenchmarkResultListItem[];
  onSelectResult: (filename: string) => void;
  selectedFilename?: string;
}

export default function BenchmarkHistoryList({
  results,
  onSelectResult,
  selectedFilename,
}: BenchmarkHistoryListProps) {
  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card className="w-full h-full">
      <CardHeader>
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <History className="w-5 h-5" />
          Benchmark History
        </h3>
        <p className="text-sm text-muted-foreground">
          {results.length} benchmark run(s)
        </p>
      </CardHeader>
      <CardContent className="p-0">
        {results.length === 0 ? (
          <div className="text-center text-muted-foreground p-8 italic">
            No benchmark results yet
          </div>
        ) : (
          <div className="max-h-[600px] overflow-y-auto">
            {results.map((result) => (
              <div
                key={result.filename}
                onClick={() => onSelectResult(result.filename)}
                className={`p-4 border-b cursor-pointer hover:bg-muted/50 transition-colors ${
                  selectedFilename === result.filename
                    ? 'bg-muted border-l-4 border-l-primary'
                    : ''
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">
                        {result.pmcid}
                      </span>
                      <span
                        className={`text-lg font-bold ${getScoreColor(result.average_score)}`}
                      >
                        {(result.average_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {new Date(result.timestamp).toLocaleString()}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {result.total_tasks} task(s) benchmarked
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
