from enum import Enum
from openai import AsyncOpenAI
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
    OPENAI_GPT_5 = "gpt-5"
    OPENAI_GPT_5_1 = "gpt-5.1"
    OPENAI_GPT_5_MINI = "gpt-5-mini"
    OPENAI_GPT_5_PRO = "gpt-5-pro"


async def generate_response(
    prompt: str,
    text: str,
    model: Model,
    response_format: dict | None = None,
    temperature: float = 0.0,
) -> str:
    """
    Generate a response using OpenAI API.

    Args:
        prompt: The system/instruction prompt
        text: The user input text
        model: The model to use
        response_format: Optional JSON schema for structured output
        temperature: Sampling temperature (0.0-2.0). Default 0.0 for reproducibility.
                    Lower values = more deterministic, higher = more creative.

    Returns:
        Generated response text
    """
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    # Combine the prompt with the text
    full_prompt = f"{prompt}\n\n{text}"

    # change temperature if not supported by model
    temperature_unsupported_models = {
        Model.OPENAI_GPT_5_MINI,
        Model.OPENAI_GPT_5,
        Model.OPENAI_GPT_5_PRO,
        Model.OPENAI_GPT_5_1,
    }
    if model in temperature_unsupported_models:
        temperature = 1  # default temperature for these models

    params = {
        "model": model.value,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": temperature,
    }

    # Add response_format if structured output is requested
    if response_format:
        params["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "schema": response_format,
            },
        }

    response = await client.chat.completions.create(**params)

    return response.choices[0].message.content
