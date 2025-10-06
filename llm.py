from litellm import completion
from enum import Enum

from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class Model(Enum):
    OPENAI_GPT_4 = "gpt-4"
    ANTHROPIC_CLAUDE_2 = "claude-2"
    ANTHROPIC_CLAUDE_INSTANT_100K = "claude-instant-100k"


def generate_response(prompt: str, model: Model):
    print(model, prompt)
    return {"output": "todo"}
