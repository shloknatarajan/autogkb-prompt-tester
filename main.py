from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm import Model, generate_response

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str
    text: str
    model: Model
    structured_output_class: str | None = None


class PromptResponse(BaseModel):
    output: str


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/test-prompt", response_model=PromptResponse)
async def test_prompt(request: PromptRequest):
    try:
        output = generate_response(
            prompt=request.prompt,
            text=request.text,
            model=request.model
        )
        return {"output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
