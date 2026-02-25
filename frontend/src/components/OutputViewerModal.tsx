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

interface OutputFile {
  filename: string;
  created: string;
  modified: string;
  size: number;
}

interface OutputData {
  var_pheno_ann?: any[];
  var_drug_ann?: any[];
  var_fa_ann?: any[];
  pmcid?: string;
  timestamp?: string;
  prompts_used?: { [key: string]: string };
  input_text?: string;
  [key: string]: any;
}

interface PipelineRun {
  directory: string;
  timestamp: string;
  display_date: string;
  pmcid_count: number;
  has_combined: boolean;
}

interface PipelineFile {
  filename: string;
  pmcid: string | null;
  type: "pmcid" | "combined";
  modified: string;
  size: number;
}

interface OutputViewerModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function OutputViewerModal({
  open,
  onOpenChange,
}: OutputViewerModalProps) {
  const [files, setFiles] = useState<OutputFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [outputData, setOutputData] = useState<OutputData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Pipeline outputs state
  const [viewMode, setViewMode] = useState<"single" | "pipeline">("single");
  const [pipelineRuns, setPipelineRuns] = useState<PipelineRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [runFiles, setRunFiles] = useState<PipelineFile[]>([]);
  const [selectedPipelineFile, setSelectedPipelineFile] = useState<string | null>(null);
  const [pipelineOutputData, setPipelineOutputData] = useState<OutputData | null>(null);
  const [loadingRuns, setLoadingRuns] = useState(false);
  const [loadingRunFiles, setLoadingRunFiles] = useState(false);

  // Load data when modal opens or view mode changes
  useEffect(() => {
    if (open) {
      if (viewMode === "single") {
        loadOutputFiles();
      } else {
        loadPipelineRuns();
      }
    }
  }, [open, viewMode]);

  // Reset pipeline state when modal closes
  useEffect(() => {
    if (!open) {
      setSelectedRun(null);
      setRunFiles([]);
      setSelectedPipelineFile(null);
      setPipelineOutputData(null);
    }
  }, [open]);

  const loadOutputFiles = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await fetch("http://localhost:8000/outputs");
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setFiles(data.files);

      // Auto-select first file if available
      if (data.files.length > 0 && !selectedFile) {
        loadOutputFile(data.files[0].filename);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const loadOutputFile = async (filename: string) => {
    try {
      setLoading(true);
      setError("");
      setSelectedFile(filename);
      const response = await fetch(`http://localhost:8000/outputs/${filename}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setOutputData(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // Pipeline API functions
  const loadPipelineRuns = async () => {
    try {
      setLoadingRuns(true);
      setError("");
      const response = await fetch("http://localhost:8000/pipeline-outputs");
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setPipelineRuns(data.runs);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoadingRuns(false);
    }
  };

  const loadRunFiles = async (runDirectory: string) => {
    try {
      setLoadingRunFiles(true);
      setError("");
      const response = await fetch(`http://localhost:8000/pipeline-outputs/${runDirectory}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setRunFiles(data.files);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoadingRunFiles(false);
    }
  };

  const loadPipelineFile = async (runDirectory: string, filename: string) => {
    try {
      setLoading(true);
      setError("");
      setSelectedPipelineFile(filename);
      const response = await fetch(`http://localhost:8000/pipeline-outputs/${runDirectory}/${filename}`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setPipelineOutputData(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const toggleRunExpand = async (runDirectory: string) => {
    if (selectedRun === runDirectory) {
      // Collapse
      setSelectedRun(null);
      setRunFiles([]);
      setSelectedPipelineFile(null);
      setPipelineOutputData(null);
    } else {
      // Expand and load files
      setSelectedRun(runDirectory);
      setSelectedPipelineFile(null);
      setPipelineOutputData(null);
      await loadRunFiles(runDirectory);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const copyToClipboard = async (data: OutputData | null) => {
    if (!data) return;

    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      alert("JSON copied to clipboard!");
    } catch (err) {
      alert("Failed to copy to clipboard");
    }
  };

  const renderAnnotations = (data: OutputData | null) => {
    if (!data) return null;

    const annotationTypes = [
      { key: "var_pheno_ann", label: "Variant-Phenotype Annotations" },
      { key: "var_drug_ann", label: "Variant-Drug Annotations" },
      { key: "var_fa_ann", label: "Variant-Functional Annotations" },
      { key: "study_parameters", label: "Study Parameters" },
    ];

    return (
      <div className="space-y-6">
        {annotationTypes.map(({ key, label }) => {
          const annotations = data[key];
          if (!annotations || !Array.isArray(annotations)) return null;

          return (
            <div key={key}>
              <h3 className="text-lg font-semibold mb-3">{label}</h3>
              <div className="space-y-3">
                {annotations.map((ann: any, index: number) => (
                  <Card key={index} className="p-4">
                    <div className="space-y-2 text-sm">
                      {Object.entries(ann).map(([field, value]) => {
                        // Handle Citations array specially
                        if (field === "Citations" && Array.isArray(value)) {
                          return (
                            <div key={field}>
                              <span className="font-medium">{field}:</span>
                              <ul className="list-disc list-inside ml-4 mt-1">
                                {value.map((citation: string, i: number) => (
                                  <li key={i} className="text-muted-foreground">
                                    {citation}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          );
                        }

                        // Handle regular fields
                        return (
                          <div key={field}>
                            <span className="font-medium">{field}:</span>{" "}
                            <span className="text-muted-foreground">
                              {typeof value === "object"
                                ? JSON.stringify(value)
                                : String(value)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderSummary = (data: OutputData | null) => {
    if (!data) return null;

    const varPhenoCount = data.var_pheno_ann?.length || 0;
    const varDrugCount = data.var_drug_ann?.length || 0;
    const varFaCount = data.var_fa_ann?.length || 0;
    const totalAnnotations = varPhenoCount + varDrugCount + varFaCount;

    return (
      <div className="space-y-4">
        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-3">Overview</h3>
          <div className="space-y-2 text-sm">
            {data.pmcid && (
              <div>
                <span className="font-medium">PMCID:</span>{" "}
                <span className="text-muted-foreground">
                  {data.pmcid}
                </span>
              </div>
            )}
            {data.timestamp && (
              <div>
                <span className="font-medium">Generated:</span>{" "}
                <span className="text-muted-foreground">
                  {formatDate(data.timestamp)}
                </span>
              </div>
            )}
            <div>
              <span className="font-medium">Total Annotations:</span>{" "}
              <span className="text-muted-foreground">{totalAnnotations}</span>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-3">Annotation Counts</h3>
          <div className="space-y-2 text-sm">
            <div>
              <span className="font-medium">Variant-Phenotype:</span>{" "}
              <span className="text-muted-foreground">{varPhenoCount}</span>
            </div>
            <div>
              <span className="font-medium">Variant-Drug:</span>{" "}
              <span className="text-muted-foreground">{varDrugCount}</span>
            </div>
            <div>
              <span className="font-medium">
                Variant-Functional Annotations:
              </span>{" "}
              <span className="text-muted-foreground">{varFaCount}</span>
            </div>
          </div>
        </Card>

        {data.prompts_used && (
          <Card className="p-4">
            <h3 className="text-lg font-semibold mb-3">Prompts Used</h3>
            <div className="space-y-2 text-sm">
              {Object.entries(data.prompts_used).map(([task, prompt]) => (
                <div key={task}>
                  <span className="font-medium">{task}:</span>{" "}
                  <span className="text-muted-foreground">{prompt}</span>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    );
  };

  // Render the content viewer (Summary/Annotations/JSON tabs)
  const renderContentViewer = (data: OutputData | null, isLoading: boolean) => {
    if (!data && !isLoading) {
      return (
        <p className="text-muted-foreground">
          Select an output file to view
        </p>
      );
    }
    if (isLoading) {
      return <p className="text-muted-foreground">Loading output...</p>;
    }
    if (!data) return null;

    return (
      <Tabs defaultValue="summary">
        <TabsList>
          <TabsTrigger value="summary">Summary</TabsTrigger>
          <TabsTrigger value="annotations">Annotations</TabsTrigger>
          <TabsTrigger value="json">JSON</TabsTrigger>
        </TabsList>

        <TabsContent
          value="summary"
          className="max-h-[60vh] overflow-y-auto flex-1"
        >
          {renderSummary(data)}
        </TabsContent>

        <TabsContent
          value="annotations"
          className="max-h-[60vh] overflow-y-auto flex-1"
        >
          {renderAnnotations(data)}
        </TabsContent>

        <TabsContent
          value="json"
          className="max-h-[60vh] overflow-auto flex-1 min-w-0"
        >
          <Button
            onClick={() => copyToClipboard(data)}
            variant="outline"
            size="sm"
            className="mb-3"
          >
            Copy JSON
          </Button>
          <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto flex-1 min-w-0">
            {JSON.stringify(data, null, 2)}
          </pre>
        </TabsContent>
      </Tabs>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[90vw] max-h-[90vh] min-h-[70vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Output Viewer</DialogTitle>
        </DialogHeader>

        {/* Top-level tabs for Single vs Pipeline outputs */}
        <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as "single" | "pipeline")} className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="mb-4 w-fit">
            <TabsTrigger value="single">Single Outputs</TabsTrigger>
            <TabsTrigger value="pipeline">Pipeline Runs</TabsTrigger>
          </TabsList>

          {/* Single Outputs Tab */}
          <TabsContent value="single" className="flex-1 overflow-hidden mt-0">
            <div className="flex gap-4 h-full overflow-hidden">
              {/* Left sidebar - File list */}
              <div className="w-64 border-r pr-4 overflow-y-auto">
                <h3 className="font-semibold mb-3">Saved Outputs</h3>
                {loading && files.length === 0 && (
                  <p className="text-sm text-muted-foreground">Loading...</p>
                )}
                {error && (
                  <p className="text-sm text-destructive">Error: {error}</p>
                )}
                {files.length === 0 && !loading && (
                  <p className="text-sm text-muted-foreground">
                    No outputs found. Run best prompts to generate outputs.
                  </p>
                )}
                <div className="space-y-2">
                  {files.map((file) => (
                    <Button
                      key={file.filename}
                      variant={
                        selectedFile === file.filename ? "default" : "outline"
                      }
                      className="w-full justify-start text-left h-auto py-2"
                      onClick={() => loadOutputFile(file.filename)}
                    >
                      <div className="flex flex-col items-start gap-1 w-full">
                        <span className="font-medium text-sm truncate w-full">
                          {file.filename.replace(".json", "")}
                        </span>
                        <span className="text-xs opacity-70">
                          {formatDate(file.modified)}
                        </span>
                        <span className="text-xs opacity-70">
                          {formatFileSize(file.size)}
                        </span>
                      </div>
                    </Button>
                  ))}
                </div>
              </div>

              {/* Right content - Tabs */}
              <div className="flex-1 flex flex-col min-h-0 min-w-0">
                {renderContentViewer(outputData, loading)}
              </div>
            </div>
          </TabsContent>

          {/* Pipeline Runs Tab */}
          <TabsContent value="pipeline" className="flex-1 overflow-hidden mt-0">
            <div className="flex gap-4 h-full overflow-hidden">
              {/* Left sidebar - Pipeline runs list */}
              <div className="w-72 border-r pr-4 overflow-y-auto">
                <h3 className="font-semibold mb-3">Pipeline Runs</h3>
                {loadingRuns && (
                  <p className="text-sm text-muted-foreground">Loading...</p>
                )}
                {error && (
                  <p className="text-sm text-destructive">Error: {error}</p>
                )}
                {pipelineRuns.length === 0 && !loadingRuns && (
                  <p className="text-sm text-muted-foreground">
                    No pipeline runs found.
                  </p>
                )}
                <div className="space-y-1">
                  {pipelineRuns.map((run) => (
                    <div key={run.directory} className="border rounded-lg overflow-hidden">
                      {/* Collapsible header */}
                      <button
                        onClick={() => toggleRunExpand(run.directory)}
                        className="w-full flex items-center justify-between p-3 hover:bg-muted/50 transition-colors text-left"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-xs">
                            {selectedRun === run.directory ? "▼" : "▶"}
                          </span>
                          <span className="font-medium text-sm">{run.display_date}</span>
                        </div>
                        <span className="text-xs bg-muted px-2 py-1 rounded">
                          {run.pmcid_count}
                        </span>
                      </button>

                      {/* Expanded content - file list */}
                      {selectedRun === run.directory && (
                        <div className="pl-6 pr-2 pb-2 space-y-1">
                          {loadingRunFiles ? (
                            <p className="text-xs text-muted-foreground py-2">Loading...</p>
                          ) : (
                            runFiles.map((file) => (
                              <button
                                key={file.filename}
                                onClick={() => loadPipelineFile(run.directory, file.filename)}
                                className={`w-full text-left px-3 py-1.5 text-sm rounded transition-colors ${
                                  selectedPipelineFile === file.filename
                                    ? "bg-primary text-primary-foreground"
                                    : "hover:bg-muted"
                                } ${file.type === "combined" ? "italic text-muted-foreground" : ""}`}
                              >
                                {file.type === "combined" ? "[Combined Output]" : file.pmcid}
                              </button>
                            ))
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Right content - Output viewer */}
              <div className="flex-1 flex flex-col min-h-0 min-w-0">
                {renderContentViewer(pipelineOutputData, loading)}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
