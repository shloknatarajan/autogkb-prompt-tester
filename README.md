# AutoGKB Prompt Tester

A multi-prompt testing application that allows you to test and compare multiple LLM prompts simultaneously. Built with FastAPI (backend) and React (frontend).

## Architecture

### Frontend (`/frontend`)
- **React** with functional components and hooks
- **Vite** for fast development and building

### Backend (`/`)
- **FastAPI** for API endpoints
- **OpenAI API** for LLM interactions
- **Pydantic** for data validation

## Prerequisites

- **Python** 3.13+
- **Node.js** 18+
- **pixi** package manager
- **OpenAI API key**

## Installation

### 1. Clone the repository
```bash
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


Run backend:
```bash
pixi run backend
# or
pixi run be
```

Run frontend:
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

- Avi Udash <udashavi@gmail.com>
- Shlok Natarajan <shlok.natarajan@gmail.com>

