from litellm import completion
from enum import Enum
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class Model(Enum):
    OPENAI_GPT_4 = "gpt-4"
    ANTHROPIC_CLAUDE_2 = "claude-2"
    ANTHROPIC_CLAUDE_INSTANT_100K = "claude-instant-100k"
