# AutoGKB Prompt Tester

A multi-prompt testing application that allows you to test and compare multiple LLM prompts simultaneously. Built with FastAPI (backend) and React (frontend).

## Features

- 🚀 **Multi-Prompt Testing**: Create and test multiple prompts against the same input text
- 📊 **Side-by-Side Comparison**: View all prompt outputs in a dedicated sidebar for easy comparison
- 💾 **Persistent Storage**: Save prompts and outputs to JSON for later analysis
- 🎯 **Structured Output Support**: Configure custom JSON schemas for structured responses
- 🔄 **Batch Execution**: Run all prompts sequentially with a single click
- 🎨 **Clean UI**: Three-panel layout with prompts list, configuration, and outputs

## Architecture

### Frontend (`/frontend`)
- **React** with functional components and hooks
- **Vite** for fast development and building
- **Component-based architecture**:
  - `PromptsSidebar`: Manage prompt list
  - `OutputsSidebar`: View all outputs
  - `PromptDetails`: Configure individual prompts
  - `usePrompts` hook: All prompt logic and API calls

### Backend (`/`)
- **FastAPI** for API endpoints
- **OpenAI API** for LLM interactions
- **Pydantic** for data validation
- **JSON file storage** for persistence

## Prerequisites

- **Python** 3.13+
- **Node.js** 18+
- **pixi** package manager
- **OpenAI API key**

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd autogkb-prompt-tester
```

### 2. Install dependencies

Using pixi (recommended):
```bash
pixi install
```

Or manually:
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 3. Set up environment variables

Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional
```

## Running the Application

### Option 1: Using pixi (Recommended)

Run both frontend and backend:
```bash
pixi run dev
# or
pixi run start
```

Run only backend:
```bash
pixi run backend
# or
pixi run be
```

Run only frontend:
```bash
pixi run frontend
# or
pixi run fe
```

### Option 2: Manual

**Backend** (in root directory):
```bash
uvicorn main:app --reload
```
Server runs on http://localhost:8000

**Frontend** (in frontend directory):
```bash
cd frontend
npm run dev
```
Server runs on http://localhost:5173

## Usage

### Creating Prompts

1. Click **"+ Add"** button in the left sidebar
2. Select a prompt from the list to configure it
3. Set the model (e.g., gpt-4o, gpt-4o-mini)
4. Optionally add a response format (JSON schema)
5. Write your prompt text

### Testing Prompts

1. Enter your input text in the **"Input Text"** field
2. Click **"Run This Prompt"** to test a single prompt
3. Click **"Run All Prompts"** to test all prompts sequentially
4. View outputs in the right sidebar

### Managing Prompts

- **Rename**: Click the prompt name in the sidebar to edit
- **Delete**: Click the **×** button next to a prompt
- **Save Individual**: Click **"Save"** button in the output preview
- **Save All**: Click **"Save All Prompts"** at the bottom of the outputs sidebar

### Structured Output

To use structured output with JSON schemas:

1. In the **"Response Format"** field, enter a JSON schema:
```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "response",
    "schema": {
      "type": "object",
      "properties": {
        "variants": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "variant": {"type": "string"},
              "gene": {"type": "string"},
              "allele": {"type": "string"}
            },
            "required": ["variant", "gene"]
          }
        }
      }
    }
  }
}
```

2. The API will enforce this schema in the response

## API Endpoints

### `GET /healthcheck`
Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

### `POST /test-prompt`
Test a single prompt against input text.

**Request:**
```json
{
  "prompt": "Extract entities from this text",
  "text": "Input text here",
  "model": "gpt-4o-mini",
  "response_format": {"type": "json_object"}
}
```

**Response:**
```json
{
  "output": "LLM response here"
}
```

### `POST /save-prompt`
Save a single prompt with its output.

**Request:**
```json
{
  "prompt": "Extract entities",
  "text": "Input text",
  "model": "gpt-4o-mini",
  "response_format": null,
  "output": "Result"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Prompt saved successfully"
}
```

### `POST /save-all-prompts`
Save all current prompts (overwrites stored_prompts.json).

**Request:**
```json
{
  "prompts": [
    {
      "name": "Prompt 1",
      "prompt": "Extract entities",
      "model": "gpt-4o-mini",
      "responseFormat": "",
      "output": "Result"
    }
  ],
  "text": "Input text"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Saved 1 prompts successfully"
}
```

### `GET /prompts`
Retrieve all saved prompts.

**Response:**
```json
{
  "prompts": [
    {
      "prompt": "Extract entities",
      "text": "Input text",
      "model": "gpt-4o-mini",
      "response_format": null,
      "output": "Result",
      "timestamp": "2025-01-15T10:30:00"
    }
  ]
}
```

## File Structure

```
autogkb-prompt-tester/
├── utils/                           # Shared utilities (NEW)
│   ├── config.py                   # Centralized configuration
│   ├── benchmark_runner.py         # Benchmark execution
│   ├── prompt_manager.py           # Prompt loading/selection
│   ├── citation_generator.py       # Citation generation
│   ├── output_manager.py           # Output file handling
│   └── normalization.py            # Term normalization
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PromptsSidebar.tsx   # Left sidebar - prompt list
│   │   │   ├── OutputsSidebar.tsx   # Right sidebar - outputs
│   │   │   └── PromptDetails.tsx    # Main content - prompt config
│   │   ├── hooks/
│   │   │   └── usePrompts.ts        # Custom hook for prompt logic
│   │   ├── App.tsx                  # Main app component
│   │   └── main.tsx                 # Entry point
│   ├── package.json
│   └── vite.config.ts
│
├── benchmarks/                      # Evaluation system
│   ├── pheno_benchmark.py
│   ├── drug_benchmark.py
│   └── fa_benchmark.py
│
├── scripts/                         # CLI automation (thin wrappers)
│   ├── run_benchmark.py
│   ├── combine_outputs.py
│   ├── normalize_terms.py
│   ├── batch_process.py
│   └── full-benchmark-pipeline.py
│
├── term_normalization/              # Term standardization
├── data/                            # Input data
├── persistent_data/                 # Ground truth
├── outputs/                         # Generated annotations
├── benchmark_results/               # Evaluation results
│
├── main.py                          # FastAPI backend (~1,100 lines)
├── llm.py                           # LLM API integration
├── stored_prompts.json             # Saved prompts (auto-generated)
├── best_prompts.json               # Best prompt configuration
├── pixi.toml                       # Pixi configuration
├── .env                            # Environment variables (create this)
├── CLAUDE.md                       # Comprehensive project documentation
└── README.md                       # This file
```

## Data Storage

Prompts are stored in `stored_prompts.json` with the following structure:

```json
[
  {
    "prompt": "Your prompt text",
    "text": "Input text used",
    "model": "gpt-4o-mini",
    "response_format": {
      "type": "json_object"
    },
    "output": "LLM response or JSON object",
    "timestamp": "2025-01-15T10:30:00.123456"
  }
]
```

## Supported Models

- `gpt-4o`
- `gpt-4o-mini`
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

## Code Organization

### Shared Utilities Architecture

The project follows a **shared utilities pattern** to eliminate code duplication:

**Key Benefits:**
- Single source of truth for common operations
- Consistent behavior between FastAPI backend and CLI scripts
- ~800 lines of duplicated code eliminated
- All critical bugs fixed (path handling, ground truth loading)

**Utility Modules:**
- `utils/benchmark_runner.py` - Benchmark execution with automatic ground truth fallback
- `utils/prompt_manager.py` - Prompt loading and selection
- `utils/citation_generator.py` - Citation generation with shared template
- `utils/output_manager.py` - File I/O with validation
- `utils/normalization.py` - Term normalization helpers
- `utils/config.py` - Centralized configuration constants

Both `main.py` and CLI scripts import from these utilities, ensuring identical behavior.

See `CLAUDE.md` for detailed documentation of all components.

## Development

### Adding New Components

1. Create component in `frontend/src/components/`
2. Import and use in `App.tsx`
3. Add props and callbacks as needed

### Adding New API Endpoints

1. Define Pydantic model in `main.py`
2. Create endpoint function with `@app.post()` or `@app.get()`
3. Consider adding corresponding utility in `utils/` if logic is reusable
4. Add corresponding function in `usePrompts.ts` hook
5. Update documentation

### Using Shared Utilities

When adding new features, check if utilities already exist:

```python
# Good: Use shared utility
from utils.benchmark_runner import BenchmarkRunner
runner = BenchmarkRunner()

# Bad: Duplicate benchmarking logic
# Don't copy-paste code from main.py or scripts
```

### Styling

All styles are in `frontend/src/index.css`. The app uses Tailwind CSS with a two-tab interface:
- Prompt Testing Tab: Three-column layout (prompts | config | outputs)
- Benchmarks Tab: Two sub-tabs (single | pipeline)

## Troubleshooting

### Backend won't start
- Check that `.env` file exists with valid API keys
- Ensure Python 3.13+ is installed
- Verify all dependencies are installed: `pixi install`

### Frontend won't start
- Ensure Node.js 18+ is installed
- Run `npm install` in the `frontend` directory
- Check that backend is running on port 8000

### CORS errors
- Ensure backend is running on `localhost:8000`
- Frontend must run on `localhost:5173`
- Check CORS middleware in `main.py`

### Prompts not loading
- Check that `stored_prompts.json` exists
- Verify backend `/prompts` endpoint is accessible
- Check browser console for errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License

## Authors

- Shlok Natarajan <shlok.natarajan@gmail.com>
- Built with Claude Code

---

**Note**: This is a development tool. Do not expose to production without proper authentication and rate limiting.
