from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class Model(str, Enum):
    OPENAI_GPT_4 = "gpt-4"
    OPENAI_GPT_4_TURBO = "gpt-4-turbo"
    OPENAI_GPT_4O = "gpt-4o"
    OPENAI_GPT_4O_MINI = "gpt-4o-mini"
    OPENAI_GPT_35_TURBO = "gpt-3.5-turbo"


def generate_response(prompt: str, text: str, model: Model) -> str:
    """Generate a response using OpenAI API."""
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Combine the prompt with the text
    full_prompt = f"{prompt}\n\n{text}"

    response = client.chat.completions.create(
        model=model.value,
        messages=[
            {"role": "user", "content": full_prompt}
        ]
    )

    return response.choices[0].message.content
