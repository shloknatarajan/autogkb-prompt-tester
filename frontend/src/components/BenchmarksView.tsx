import { useState } from 'react';
import { useBenchmarks } from '../hooks/useBenchmarks';
import { usePipeline } from '../hooks/usePipeline';
import BenchmarkRunner from './BenchmarkRunner';
import BenchmarkResultsTable from './BenchmarkResultsTable';
import BenchmarkHistoryList from './BenchmarkHistoryList';
import BenchmarkDetailModal from './BenchmarkDetailModal';
import PipelineRunner from './PipelineRunner';
import { BenchmarkTaskResult } from '../types';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function BenchmarksView() {
  const {
    benchmarkResults,
    selectedResult,
    outputFiles,
    loading,
    error,
    loadBenchmarkDetail,
    runBenchmark,
    benchmarkFromOutput,
  } = useBenchmarks();

  const {
    jobs: pipelineJobs,
    currentJob: currentPipelineJob,
    loading: pipelineLoading,
    error: pipelineError,
    startPipeline,
    selectJob: selectPipelineJob,
  } = usePipeline();

  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [detailTask, setDetailTask] = useState<string>('');
  const [detailResult, setDetailResult] = useState<BenchmarkTaskResult | null>(
    null,
  );
  const [selectedFilename, setSelectedFilename] = useState<string | undefined>(
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
              onRunBenchmark={runBenchmark}
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

          <TabsContent value="pipeline">
            <PipelineRunner
              currentJob={currentPipelineJob}
              jobs={pipelineJobs}
              loading={pipelineLoading}
              error={pipelineError}
              onStartPipeline={startPipeline}
              onSelectJob={selectPipelineJob}
            />
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
