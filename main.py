from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import Model, generate_response
import json
import os
from datetime import datetime
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File path for storing prompts
PROMPTS_FILE = "stored_prompts.json"


class PromptRequest(BaseModel):
    prompt: str
    text: str
    model: Model
    response_format: dict | None = None


class PromptResponse(BaseModel):
    output: str


class SavePromptRequest(BaseModel):
    prompt: str
    text: str
    model: Model
    response_format: dict | None = None
    output: str


class SaveAllPromptsRequest(BaseModel):
    prompts: list[dict]
    text: str


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/test-prompt", response_model=PromptResponse)
async def test_prompt(request: PromptRequest):
    try:
        response_format = None

        # Use custom response format if provided, otherwise fall back to structured_output flag
        if request.response_format:
            response_format = request.response_format

        output = generate_response(
            prompt=request.prompt,
            text=request.text,
            model=request.model,
            response_format=response_format,
        )
        return {"output": output}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-prompt")
async def save_prompt(request: SavePromptRequest):
    try:
        # Read existing prompts
        if os.path.exists(PROMPTS_FILE):
            with open(PROMPTS_FILE, 'r') as f:
                prompts = json.load(f)
        else:
            prompts = []

        # Try to parse output as JSON if possible
        try:
            parsed_output = json.loads(request.output)
        except:
            parsed_output = request.output

        # Create new prompt entry
        new_prompt = {
            "prompt": request.prompt,
            "text": request.text,
            "model": request.model,
            "response_format": request.response_format,
            "output": parsed_output,
            "timestamp": datetime.now().isoformat()
        }

        # Append new prompt
        prompts.append(new_prompt)

        # Save back to file
        with open(PROMPTS_FILE, 'w') as f:
            json.dump(prompts, f, indent=2)

        return {"status": "success", "message": "Prompt saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prompts")
async def get_prompts():
    try:
        if os.path.exists(PROMPTS_FILE):
            with open(PROMPTS_FILE, 'r') as f:
                prompts = json.load(f)
            return {"prompts": prompts}
        else:
            return {"prompts": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-all-prompts")
async def save_all_prompts(request: SaveAllPromptsRequest):
    try:
        saved_prompts = []

        for prompt_data in request.prompts:
            # Try to parse output as JSON if possible
            try:
                parsed_output = json.loads(prompt_data['output']) if prompt_data.get('output') else None
            except:
                parsed_output = prompt_data.get('output')

            # Try to parse response format if it's a string
            response_format = prompt_data.get('responseFormat')
            if response_format and isinstance(response_format, str):
                try:
                    response_format = json.loads(response_format)
                except:
                    response_format = None

            saved_prompt = {
                "prompt": prompt_data.get('prompt', ''),
                "text": request.text,
                "model": prompt_data.get('model', 'gpt-4o-mini'),
                "response_format": response_format,
                "output": parsed_output,
                "timestamp": datetime.now().isoformat()
            }
            saved_prompts.append(saved_prompt)

        # Overwrite the file with current prompts
        with open(PROMPTS_FILE, 'w') as f:
            json.dump(saved_prompts, f, indent=2)

        return {"status": "success", "message": f"Saved {len(saved_prompts)} prompts successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
