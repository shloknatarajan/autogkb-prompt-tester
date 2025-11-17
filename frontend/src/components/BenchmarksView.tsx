import { useState } from 'react';
import { useBenchmarks } from '../hooks/useBenchmarks';
import { usePipeline } from '../hooks/usePipeline';
import BenchmarkRunner from './BenchmarkRunner';
import BenchmarkResultsTable from './BenchmarkResultsTable';
import BenchmarkHistoryList from './BenchmarkHistoryList';
import BenchmarkDetailModal from './BenchmarkDetailModal';
import PipelineRunner from './PipelineRunner';
import PipelineBenchmarkResults from './PipelineBenchmarkResults';
import { BenchmarkTaskResult } from '../types';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { FileText, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function BenchmarksView() {
  const {
    benchmarkResults,
    selectedResult,
    outputFiles,
    loading,
    error,
    loadBenchmarkDetail,
    benchmarkFromOutput,
  } = useBenchmarks();

  const {
    jobs: pipelineJobs,
    currentJob: currentPipelineJob,
    pipelineResults,
    selectedPipelineResult,
    loading: pipelineLoading,
    error: pipelineError,
    startPipeline,
    selectJob: selectPipelineJob,
    loadPipelineResults,
    loadPipelineResultDetail,
    cancelJob: cancelPipelineJob,
  } = usePipeline();

  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [detailTask, setDetailTask] = useState<string>('');
  const [detailResult, setDetailResult] = useState<BenchmarkTaskResult | null>(
    null,
  );
  const [selectedFilename, setSelectedFilename] = useState<string | undefined>(
    undefined,
  );
  const [selectedPipelineFilename, setSelectedPipelineFilename] = useState<string | undefined>(
    undefined,
  );

  const handleViewDetails = (task: string) => {
    if (selectedResult && selectedResult.results[task]) {
      setDetailTask(task);
      setDetailResult(selectedResult.results[task]);
      setDetailModalOpen(true);
    }
  };

  const handleSelectResult = async (filename: string) => {
    setSelectedFilename(filename);
    await loadBenchmarkDetail(filename);
  };

  const handleSelectPipelineResult = async (filename: string) => {
    setSelectedPipelineFilename(filename);
    await loadPipelineResultDetail(filename);
  };

  return (
    <div className="h-full flex gap-4">
      {/* Left sidebar - History */}
      <div className="w-80 flex-shrink-0">
        <BenchmarkHistoryList
          results={benchmarkResults}
          onSelectResult={handleSelectResult}
          selectedFilename={selectedFilename}
        />
      </div>

      {/* Main content area */}
      <div className="flex-1 overflow-y-auto space-y-4">
        <Tabs defaultValue="single" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="single">Single Benchmark</TabsTrigger>
            <TabsTrigger value="pipeline">Full Pipeline</TabsTrigger>
          </TabsList>

          <TabsContent value="single" className="space-y-4">
            {/* Benchmark Runner */}
            <BenchmarkRunner
              onBenchmarkFromOutput={benchmarkFromOutput}
              outputFiles={outputFiles}
              loading={loading}
              error={error}
            />

            {/* Results Table */}
            {selectedResult && (
              <BenchmarkResultsTable
                result={selectedResult}
                onViewDetails={handleViewDetails}
              />
            )}

            {!selectedResult && benchmarkResults.length === 0 && (
              <div className="text-center text-muted-foreground p-12 italic">
                Run your first benchmark to see results here
              </div>
            )}
          </TabsContent>

          <TabsContent value="pipeline" className="space-y-4">
            <PipelineRunner
              currentJob={currentPipelineJob}
              jobs={pipelineJobs}
              loading={pipelineLoading}
              error={pipelineError}
              onStartPipeline={startPipeline}
              onSelectJob={selectPipelineJob}
              onCancelJob={cancelPipelineJob}
            />

            {/* Pipeline Results History */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Pipeline Benchmark Results
                  </h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={loadPipelineResults}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {pipelineResults.length === 0 ? (
                  <div className="text-center text-muted-foreground py-8">
                    No pipeline benchmark results yet. Run a pipeline to generate results.
                  </div>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {pipelineResults.map((result) => (
                      <div
                        key={result.filename}
                        className={`p-3 border rounded cursor-pointer hover:bg-muted/50 transition-colors ${
                          selectedPipelineFilename === result.filename
                            ? 'bg-muted border-primary'
                            : ''
                        }`}
                        onClick={() => handleSelectPipelineResult(result.filename)}
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <div className="font-medium text-sm">
                              {new Date(result.timestamp).toLocaleString()}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {result.total_pmcids} PMCIDs • {result.config.model}
                            </div>
                          </div>
                          <div className="text-lg font-bold text-primary">
                            {(result.overall_score * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Selected Pipeline Result Details */}
            {selectedPipelineResult && (
              <PipelineBenchmarkResults result={selectedPipelineResult} />
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Detail Modal */}
      <BenchmarkDetailModal
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        task={detailTask}
        result={detailResult}
      />
    </div>
  );
}
