from fastapi import FastAPI
from .llm import Model
from pydantic import BaseModel

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str
    text: str
    model: Model
    structured_output_class: str | None = None


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/test-prompt")
async def test_prompt(request: PromptRequest):
    return {"output": "todo"}
