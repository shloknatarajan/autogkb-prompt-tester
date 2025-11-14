import { useState } from "react";
import PromptsSidebar from "./components/PromptsSidebar";
import OutputsSidebar from "./components/OutputsSidebar";
import PromptDetails from "./components/PromptDetails";
import OutputViewerModal from "./components/OutputViewerModal";
import BenchmarksView from "./components/BenchmarksView";
import { usePrompts } from "./hooks/usePrompts";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const MODELS = [
  "gpt-4o",
  "gpt-4o-mini",
  "gpt-4-turbo",
  "gpt-4",
  "gpt-3.5-turbo",
  "gpt-5",
  "gpt-5-mini",
  "gpt-5-pro",
];

function App() {
  const [text, setText] = useState("");
  const [globalModel, setGlobalModel] = useState("gpt-4o-mini");
  const [selectedFileName, setSelectedFileName] = useState("");
  const [outputViewerOpen, setOutputViewerOpen] = useState(false);
  const {
    prompts,
    filteredPrompts,
    tasks,
    selectedTask,
    selectedPromptIndex,
    loading,
    error,
    bestPrompts,
    addNewPrompt,
    updatePrompt,
    deletePrompt,
    runPrompt,
    runAllPrompts,
    savePrompt,
    saveAllPrompts,
    setSelectedPromptIndex,
    setSelectedTask,
    addTask,
    deleteTask,
    renameTask,
    setBestPrompt,
    runBestPrompts,
  } = usePrompts();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setText(e.target?.result as string);
        setSelectedFileName(file.name);
      };
      reader.readAsText(file);
    }
  };

  const clearFile = () => {
    setSelectedFileName("");
    // Reset the file input
    const fileInput = document.getElementById("file-input") as HTMLInputElement;
    if (fileInput) {
      fileInput.value = "";
    }
  };

  return (
    <div className="mx-auto p-8 max-w-full">
      <h1 className="text-center text-3xl font-bold mb-6">
        AutoGKB Prompt Tester
      </h1>

      <Tabs defaultValue="prompts" className="w-full">
        <TabsList className="grid w-full max-w-md mx-auto mb-6" style={{ gridTemplateColumns: '1fr 1fr' }}>
          <TabsTrigger value="prompts">Prompt Testing</TabsTrigger>
          <TabsTrigger value="benchmarks">Benchmarks</TabsTrigger>
        </TabsList>

        <TabsContent value="prompts" className="mt-0">
          <div className="flex gap-8 h-[calc(100vh-200px)]">
            <PromptsSidebar
          prompts={filteredPrompts}
          tasks={tasks}
          selectedTask={selectedTask}
          selectedPromptIndex={selectedPromptIndex}
          onSelectPrompt={setSelectedPromptIndex}
          onAddPrompt={addNewPrompt}
          onUpdatePrompt={(index, field, value) => {
            // Find actual index in full prompts array
            const actualIndex = prompts.findIndex(
              (p) => p.id === filteredPrompts[index].id,
            );
            updatePrompt(actualIndex, field, value);
          }}
          onDeletePrompt={(index) => {
            const actualIndex = prompts.findIndex(
              (p) => p.id === filteredPrompts[index].id,
            );
            deletePrompt(actualIndex);
          }}
          onSelectTask={setSelectedTask}
          onAddTask={addTask}
          onDeleteTask={deleteTask}
          onRenameTask={renameTask}
          bestPrompts={bestPrompts}
          onSetBestPrompt={setBestPrompt}
          loading={loading}
          onSaveAll={() => saveAllPrompts(text)}
        />

        <div className="flex-1 flex flex-col gap-6 overflow-y-auto min-w-0">
          <div className="p-4 bg-card rounded-lg border">
            <div className="flex flex-col gap-2 mb-4">
              <Label htmlFor="model">Global Model:</Label>
              <Select value={globalModel} onValueChange={setGlobalModel}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {MODELS.map((m) => (
                    <SelectItem key={m} value={m}>
                      {m}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-2 mb-4">
              <Label htmlFor="file-input">Load from File:</Label>
              <div className="flex items-center gap-4 flex-wrap">
                <Input
                  type="file"
                  id="file-input"
                  accept=".md,.markdown"
                  onChange={handleFileSelect}
                  className="flex-1 min-w-[200px]"
                />
                {selectedFileName && (
                  <span className="inline-flex items-center gap-2 px-3 py-2 bg-primary/10 border border-primary rounded text-sm">
                    📄 {selectedFileName}
                    <Button
                      onClick={clearFile}
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0 ml-1"
                    >
                      ×
                    </Button>
                  </span>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="text">Input Text:</Label>
              <Textarea
                id="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter the text to process..."
                rows={6}
                className="min-h-[200px]"
              />
            </div>
          </div>

          {selectedPromptIndex !== null &&
            filteredPrompts[selectedPromptIndex] && (
              <PromptDetails
                prompt={filteredPrompts[selectedPromptIndex]}
                onUpdate={(field, value) => {
                  const actualIndex = prompts.findIndex(
                    (p) => p.id === filteredPrompts[selectedPromptIndex].id,
                  );
                  updatePrompt(actualIndex, field, value);
                }}
                onRun={() => {
                  const actualIndex = prompts.findIndex(
                    (p) => p.id === filteredPrompts[selectedPromptIndex].id,
                  );
                  runPrompt(actualIndex, text, globalModel);
                }}
              />
            )}

          {error && (
            <div className="p-6 rounded bg-destructive/10 border border-destructive text-destructive-foreground">
              <h3 className="font-semibold mb-2">Error:</h3>
              <p className="m-0">{error}</p>
            </div>
          )}
        </div>

        <OutputsSidebar
          prompts={filteredPrompts}
          selectedTask={selectedTask}
          onSavePrompt={(index) => {
            const actualIndex = prompts.findIndex(
              (p) => p.id === filteredPrompts[index].id,
            );
            savePrompt(actualIndex, text);
          }}
          onSaveAll={() => saveAllPrompts(text)}
          onRunAll={() => runAllPrompts(text, globalModel)}
          onRunBest={() => runBestPrompts(text, globalModel)}
          onViewOutputs={() => setOutputViewerOpen(true)}
          bestPrompts={bestPrompts}
          loading={loading}
          tasks={tasks}
        />
          </div>
        </TabsContent>

        <TabsContent value="benchmarks" className="mt-0">
          <div className="h-[calc(100vh-200px)]">
            <BenchmarksView />
          </div>
        </TabsContent>
      </Tabs>

      <OutputViewerModal
        open={outputViewerOpen}
        onOpenChange={setOutputViewerOpen}
      />
    </div>
  );
}

export default App;
