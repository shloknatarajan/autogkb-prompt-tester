import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface BenchmarkArticle {
  pmcid: string;
  title: string;
  pmid: string;
  annotation_counts: {
    var_fa_ann: number;
    var_pheno_ann: number;
    var_drug_ann: number;
  };
}

interface OutputFile {
  filename: string;
  created: string;
  modified: string;
  size: number;
}

interface BenchmarkResults {
  overall_score: number;
  total_samples: number;
  field_scores: {
    [field: string]: {
      mean_score: number;
      scores: number[];
    };
  };
}

interface HistoryEntry {
  timestamp: string;
  pmcid: string;
  prompts_used?: { [task: string]: string };
  overall_score: number;
  result_file: string;
}

interface BenchmarkModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  prompts: any[];
}

export default function BenchmarkModal({
  open,
  onOpenChange,
  prompts,
}: BenchmarkModalProps) {
  const [articles, setArticles] = useState<BenchmarkArticle[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<string>("");
  const [mode, setMode] = useState<"existing" | "run">("existing");
  const [outputFiles, setOutputFiles] = useState<OutputFile[]>([]);
  const [selectedOutput, setSelectedOutput] = useState<string>("");
  const [selectedPromptId, setSelectedPromptId] = useState<string>("");
  const [results, setResults] = useState<BenchmarkResults | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load benchmark articles and history when modal opens
  useEffect(() => {
    if (open) {
      loadBenchmarkArticles();
      loadHistory();
      loadOutputFiles();
    }
  }, [open]);

  const loadBenchmarkArticles = async () => {
    try {
      console.log("Fetching benchmark articles...");
      const response = await fetch("http://localhost:8000/benchmark-articles");
      console.log("Response status:", response.status);
      if (!response.ok) throw new Error("Failed to load benchmark articles");
      const data = await response.json();
      console.log("Raw response data:", data);
      console.log("Articles array:", data.articles);
      console.log("Articles length:", data.articles?.length);

      if (!data.articles || !Array.isArray(data.articles)) {
        console.error("Invalid data structure - articles is not an array:", data);
        setError("Invalid response from server");
        return;
      }

      setArticles(data.articles);
      if (data.articles.length > 0) {
        setSelectedArticle(data.articles[0].pmcid);
      } else {
        console.warn("No articles found in benchmark data");
      }
    } catch (err) {
      console.error("Error loading articles:", err);
      setError((err as Error).message);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch("http://localhost:8000/benchmark-history");
      if (!response.ok) throw new Error("Failed to load history");
      const data = await response.json();
      setHistory(data.history);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  };

  const loadOutputFiles = async () => {
    try {
      const response = await fetch("http://localhost:8000/outputs");
      if (!response.ok) throw new Error("Failed to load output files");
      const data = await response.json();
      setOutputFiles(data.files);
    } catch (err) {
      console.error("Failed to load output files:", err);
    }
  };

  const runBenchmarkExisting = async () => {
    if (!selectedArticle || !selectedOutput) {
      setError("Please select an article and output file");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResults(null);

      // Load the output file
      const outputResponse = await fetch(
        `http://localhost:8000/outputs/${selectedOutput}`,
      );
      if (!outputResponse.ok) throw new Error("Failed to load output file");
      const outputData = await outputResponse.json();

      // Run benchmark
      const benchmarkResponse = await fetch(
        "http://localhost:8000/run-benchmark",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            pmcid: selectedArticle,
            predictions: outputData,
          }),
        },
      );

      if (!benchmarkResponse.ok) {
        const errorData = await benchmarkResponse.json();
        throw new Error(errorData.detail || "Benchmark failed");
      }

      const data = await benchmarkResponse.json();
      setResults(data.results);
      loadHistory(); // Reload history
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const runBenchmarkWithPrompts = async () => {
    if (!selectedArticle || !selectedPromptId) {
      setError("Please select an article and prompt");
      return;
    }

    setError(
      'This feature requires article text to be available. Please use the "Evaluate Existing Output" mode for now.',
    );
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "text-green-600";
    if (score >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const varFaPrompts = prompts.filter((p) => p.task === "var-fa");

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[90vw] max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Benchmark Evaluation</DialogTitle>
        </DialogHeader>

        <Tabs
          defaultValue="run"
          className="flex-1 flex flex-col overflow-hidden"
        >
          <TabsList>
            <TabsTrigger value="run">Run Benchmark</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>

          <TabsContent value="run" className="flex-1 overflow-y-auto">
            <div className="space-y-4">
              {/* Article Selection */}
              <Card className="p-4">
                <h3 className="font-semibold mb-2">Select Benchmark Article</h3>
                <Select
                  value={selectedArticle}
                  onValueChange={setSelectedArticle}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select article..." />
                  </SelectTrigger>
                  <SelectContent>
                    {articles.map((article) => (
                      <SelectItem key={article.pmcid} value={article.pmcid}>
                        {article.pmcid} - {article.title ? article.title.substring(0, 50) : "No title"}...
                        (var_fa: {article.annotation_counts.var_fa_ann})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Card>

              {/* Mode Selection */}
              <Card className="p-4">
                <h3 className="font-semibold mb-2">Evaluation Mode</h3>
                <div className="flex gap-2">
                  <Button
                    variant={mode === "existing" ? "default" : "outline"}
                    onClick={() => setMode("existing")}
                  >
                    Evaluate Existing Output
                  </Button>
                  <Button
                    variant={mode === "run" ? "default" : "outline"}
                    onClick={() => setMode("run")}
                    disabled
                  >
                    Run and Evaluate (Coming Soon)
                  </Button>
                </div>
              </Card>

              {/* Existing Output Mode */}
              {mode === "existing" && (
                <Card className="p-4">
                  <h3 className="font-semibold mb-2">Select Output File</h3>
                  <Select
                    value={selectedOutput}
                    onValueChange={setSelectedOutput}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select output file..." />
                    </SelectTrigger>
                    <SelectContent>
                      {outputFiles.map((file) => (
                        <SelectItem key={file.filename} value={file.filename}>
                          {file.filename}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button
                    onClick={runBenchmarkExisting}
                    disabled={loading || !selectedArticle || !selectedOutput}
                    className="mt-4 w-full"
                  >
                    {loading ? "Evaluating..." : "Run Benchmark"}
                  </Button>
                </Card>
              )}

              {/* Run with Prompts Mode */}
              {mode === "run" && (
                <Card className="p-4">
                  <h3 className="font-semibold mb-2">Select Prompt</h3>
                  <Select
                    value={selectedPromptId}
                    onValueChange={setSelectedPromptId}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select var-fa prompt..." />
                    </SelectTrigger>
                    <SelectContent>
                      {varFaPrompts.map((prompt) => (
                        <SelectItem
                          key={prompt.id}
                          value={prompt.id.toString()}
                        >
                          {prompt.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button
                    onClick={runBenchmarkWithPrompts}
                    disabled={loading || !selectedArticle || !selectedPromptId}
                    className="mt-4 w-full"
                  >
                    {loading ? "Running..." : "Run and Evaluate"}
                  </Button>
                </Card>
              )}

              {/* Error Display */}
              {error && (
                <Card className="p-4 border-red-500">
                  <p className="text-red-600">{error}</p>
                </Card>
              )}

              {/* Results Display */}
              {results && (
                <Card className="p-4">
                  <h3 className="font-semibold mb-4 text-lg">Results</h3>

                  {/* Overall Score */}
                  <div className="mb-6 p-4 bg-muted rounded-lg">
                    <div className="text-sm text-muted-foreground mb-1">
                      Overall Score
                    </div>
                    <div
                      className={`text-4xl font-bold ${getScoreColor(results.overall_score)}`}
                    >
                      {(results.overall_score * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {results.total_samples} annotations evaluated
                    </div>
                  </div>

                  {/* Field Scores */}
                  <h4 className="font-semibold mb-2">Field Scores</h4>
                  <div className="space-y-2 max-h-[300px] overflow-y-auto">
                    {Object.entries(results.field_scores)
                      .sort(([, a], [, b]) => b.mean_score - a.mean_score)
                      .map(([field, scores]) => (
                        <div
                          key={field}
                          className="flex items-center justify-between p-2 bg-muted rounded"
                        >
                          <span className="text-sm font-medium">{field}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-32 h-2 bg-background rounded-full overflow-hidden">
                              <div
                                className={`h-full ${
                                  scores.mean_score >= 0.8
                                    ? "bg-green-600"
                                    : scores.mean_score >= 0.6
                                      ? "bg-yellow-600"
                                      : "bg-red-600"
                                }`}
                                style={{ width: `${scores.mean_score * 100}%` }}
                              />
                            </div>
                            <span
                              className={`text-sm font-semibold w-12 text-right ${getScoreColor(scores.mean_score)}`}
                            >
                              {(scores.mean_score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      ))}
                  </div>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="history" className="flex-1 overflow-y-auto">
            <div className="space-y-3">
              {history.length === 0 && (
                <p className="text-muted-foreground text-center py-8">
                  No benchmark history yet. Run a benchmark to see results here.
                </p>
              )}
              {history.map((entry, index) => (
                <Card key={index} className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="font-semibold">{entry.pmcid}</div>
                      <div className="text-sm text-muted-foreground">
                        {formatDate(entry.timestamp)}
                      </div>
                    </div>
                    <div
                      className={`text-2xl font-bold ${getScoreColor(entry.overall_score)}`}
                    >
                      {(entry.overall_score * 100).toFixed(1)}%
                    </div>
                  </div>
                  {entry.prompts_used && (
                    <div className="text-sm text-muted-foreground">
                      Prompts: {Object.values(entry.prompts_used).join(", ")}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
