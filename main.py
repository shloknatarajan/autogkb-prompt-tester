from fastapi import FastAPI
from .llm import Model
from pydantic import BaseModel

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/test-prompt")
async def test_prompt(prompt: str, ,structured_output_class: str | None, model: Model):
    return {"output": "todo"}
