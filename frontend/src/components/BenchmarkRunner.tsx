import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { AlertCircle, PlayCircle, CheckCircle } from 'lucide-react';

interface BenchmarkRunnerProps {
  onRunBenchmark: (text: string, pmcid: string) => Promise<any>;
  loading: boolean;
  error: string;
}

export default function BenchmarkRunner({
  onRunBenchmark,
  loading,
  error,
}: BenchmarkRunnerProps) {
  const [text, setText] = useState<string>('');
  const [pmcid, setPmcid] = useState<string>('');
  const [lastResult, setLastResult] = useState<any>(null);

  const handleRunBenchmark = async () => {
    if (!text.trim() || !pmcid.trim()) {
      alert('Please enter both text and PMCID');
      return;
    }

    try {
      const result = await onRunBenchmark(text, pmcid);
      setLastResult(result);
    } catch (err) {
      // Error is handled by the hook
      setLastResult(null);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <PlayCircle className="w-5 h-5" />
          Run Benchmark
        </h3>
        <p className="text-sm text-muted-foreground">
          Run benchmarks on best prompts against ground truth data
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">PMCID</label>
          <Input
            value={pmcid}
            onChange={(e) => setPmcid(e.target.value)}
            placeholder="e.g., PMC10786722"
            disabled={loading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Input Text</label>
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter the article text to benchmark..."
            className="min-h-[200px] font-mono text-sm"
            disabled={loading}
          />
        </div>

        <Button
          onClick={handleRunBenchmark}
          disabled={loading || !text.trim() || !pmcid.trim()}
          className="w-full bg-purple-600 hover:bg-purple-700"
        >
          {loading ? 'Running Benchmark...' : 'Run Benchmark'}
        </Button>

        {error && (
          <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div>{error}</div>
          </div>
        )}

        {lastResult && !loading && (
          <div className="flex items-start gap-2 p-3 bg-green-50 border border-green-200 rounded text-green-800 text-sm">
            <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div>
              Benchmark completed! Average score:{' '}
              <strong>
                {(lastResult.metadata.average_score * 100).toFixed(1)}%
              </strong>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
