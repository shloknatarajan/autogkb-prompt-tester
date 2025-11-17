import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AlertCircle, PlayCircle, CheckCircle, FileText } from "lucide-react";
import { Separator } from "@/components/ui/separator";

interface OutputFile {
  filename: string;
  created: string;
  modified: string;
  size: number;
}

interface BenchmarkRunnerProps {
  onRunBenchmark: (text: string, pmcid: string) => Promise<any>;
  onBenchmarkFromOutput: (filename: string) => Promise<any>;
  outputFiles: OutputFile[];
  loading: boolean;
  error: string;
}

export default function BenchmarkRunner({
  onRunBenchmark,
  onBenchmarkFromOutput,
  outputFiles,
  loading,
  error,
}: BenchmarkRunnerProps) {
  const [text, setText] = useState<string>("");
  const [pmcid, setPmcid] = useState<string>("");
  const [selectedOutputFile, setSelectedOutputFile] = useState<string>("");
  const [lastResult, setLastResult] = useState<any>(null);

  const handleRunBenchmark = async () => {
    if (!text.trim() || !pmcid.trim()) {
      alert("Please enter both text and PMCID");
      return;
    }

    try {
      const result = await onRunBenchmark(text, pmcid);
      setLastResult(result);
    } catch (err) {
      setLastResult(null);
    }
  };

  const handleBenchmarkFromFile = async () => {
    if (!selectedOutputFile) {
      alert("Please select an output file");
      return;
    }

    try {
      const result = await onBenchmarkFromOutput(selectedOutputFile);
      setLastResult(result);
    } catch (err) {
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
          Benchmark prompts against ground truth data
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Benchmark from existing output file */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            <h4 className="font-medium">Benchmark Existing Output</h4>
          </div>
          <p className="text-sm text-muted-foreground">
            Benchmark a previously generated output file (no LLM calls needed)
          </p>

          <div>
            <label className="block text-sm font-medium mb-2">
              Select Output File
            </label>
            <Select
              value={selectedOutputFile}
              onValueChange={setSelectedOutputFile}
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue placeholder="Choose an output file..." />
              </SelectTrigger>
              <SelectContent>
                {outputFiles.map((file) => (
                  <SelectItem key={file.filename} value={file.filename}>
                    <div className="flex flex-col">
                      <span className="font-medium">
                        {file.filename.replace(".json", "")}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(file.modified).toLocaleString()}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button
            onClick={handleBenchmarkFromFile}
            disabled={loading || !selectedOutputFile}
            className="w-full bg-blue-600 hover:bg-blue-700"
          >
            {loading ? "Benchmarking..." : "Benchmark from File"}
          </Button>
        </div>

        <div className="flex items-center gap-4">
          <Separator className="flex-1" />
          <span className="text-sm text-muted-foreground">OR</span>
          <Separator className="flex-1" />
        </div>

        {/* Run new benchmark with text input */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <PlayCircle className="w-4 h-4" />
            <h4 className="font-medium">Run New Benchmark</h4>
          </div>
          <p className="text-sm text-muted-foreground">
            Run best prompts on new text and benchmark the results
          </p>

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
              className="min-h-[150px] font-mono text-sm"
              disabled={loading}
            />
          </div>

          <Button
            onClick={handleRunBenchmark}
            disabled={loading || !text.trim() || !pmcid.trim()}
            className="w-full bg-purple-600 hover:bg-purple-700"
          >
            {loading ? "Running Benchmark..." : "Run New Benchmark"}
          </Button>
        </div>

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
              Benchmark completed! Average score:{" "}
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
