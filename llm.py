"""
LLM interface using LiteLLM for multi-provider support.

Supports OpenAI, Anthropic, Google Gemini, and 100+ other providers.
Model names use provider prefix format: "openai/gpt-4o", "anthropic/claude-3-5-sonnet"
"""

import json
import re
from enum import Enum
from typing import Union, Tuple
import litellm
from dotenv import load_dotenv

from utils.cost import UsageInfo, extract_usage_from_response

load_dotenv()

# LiteLLM reads API keys from environment variables:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
# - GEMINI_API_KEY (for Google)

# Enable client-side JSON validation for providers without native support
litellm.enable_json_schema_validation = True

litellm.drop_params = True  # Drop unsupported params automatically


# DEPRECATED: Keep Model enum for backward compatibility
# New code should use string model names with provider prefix
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


# Temperature override for specific models that don't support temperature control
TEMPERATURE_OVERRIDES = {
    "openai/gpt-5": 1.0,
    "openai/gpt-5.1": 1.0,
    "openai/gpt-5-mini": 1.0,
    "openai/gpt-5-pro": 1.0,
}

# Providers that support OpenAI-style json_schema structured output
PROVIDERS_WITH_NATIVE_JSON_SCHEMA = {"openai"}


def normalize_model(model: str | Model) -> str:
    """
    Normalize model identifier to provider-prefixed format.

    Args:
        model: Model enum value, unprefixed string, or provider-prefixed string

    Returns:
        Provider-prefixed model string (e.g., "openai/gpt-4o")

    Examples:
        >>> normalize_model(Model.OPENAI_GPT_4O)
        'openai/gpt-4o'
        >>> normalize_model("gpt-4o")
        'openai/gpt-4o'
        >>> normalize_model("anthropic/claude-3-5-sonnet")
        'anthropic/claude-3-5-sonnet'
    """
    # Convert enum to string value
    if isinstance(model, Model):
        model_str = model.value
    else:
        model_str = model

    # Auto-prefix unprefixed models with 'openai/'
    if "/" not in model_str:
        return f"openai/{model_str}"

    return model_str


def get_provider(model_str: str) -> str:
    """Extract provider name from model string."""
    if "/" in model_str:
        return model_str.split("/")[0]
    return "openai"


def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON from a response that may contain markdown code blocks or other text.

    Args:
        response_text: Raw response text from the model

    Returns:
        Extracted JSON string
    """
    # Try to find JSON in markdown code blocks first
    json_block_pattern = r"```(?:json)?\s*\n?([\s\S]*?)\n?```"
    matches = re.findall(json_block_pattern, response_text)
    if matches:
        # Return the first valid JSON block
        for match in matches:
            try:
                json.loads(match.strip())
                return match.strip()
            except json.JSONDecodeError:
                continue

    # Try to find JSON object/array directly
    # Look for content starting with { or [
    response_text = response_text.strip()
    if response_text.startswith("{") or response_text.startswith("["):
        return response_text

    # Try to extract JSON object from anywhere in the text
    json_obj_pattern = r"(\{[\s\S]*\})"
    obj_matches = re.findall(json_obj_pattern, response_text)
    if obj_matches:
        # Return the longest valid JSON match
        for match in sorted(obj_matches, key=len, reverse=True):
            try:
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue

    # Return original if no JSON found
    return response_text


async def generate_response(
    prompt: str,
    text: str,
    model: str | Model,
    response_format: dict | None = None,
    temperature: float = 0.0,
    max_tokens: int = 16384,
    return_usage: bool = False,
) -> Union[str, Tuple[str, UsageInfo]]:
    """
    Generate a response using LiteLLM (supports multiple providers).

    Args:
        prompt: The system/instruction prompt
        text: The user input text
        model: Model identifier - can be:
            - Model enum (deprecated): Model.OPENAI_GPT_4O
            - Unprefixed string (auto-prefixes with openai/): "gpt-4o"
            - Provider-prefixed string: "openai/gpt-4o", "anthropic/claude-3-5-sonnet"
        response_format: Optional JSON schema for structured output
        temperature: Sampling temperature (0.0-2.0 for OpenAI, 0.0-1.0 for Anthropic)
                    Default 0.0 for reproducibility.
        max_tokens: Maximum tokens in the response. Default 16384 to prevent truncation.
        return_usage: If True, returns (response_text, UsageInfo) tuple for cost tracking.

    Returns:
        Generated response text, or (text, UsageInfo) tuple if return_usage=True

    Examples:
        # Using provider prefix (recommended)
        response = await generate_response(prompt, text, "anthropic/claude-3-5-sonnet")

        # Using unprefixed (defaults to OpenAI)
        response = await generate_response(prompt, text, "gpt-4o")

        # Using enum (deprecated, for backward compatibility)
        response = await generate_response(prompt, text, Model.OPENAI_GPT_4O)
    """
    # Normalize model to provider-prefixed format
    model_str = normalize_model(model)
    provider = get_provider(model_str)

    # Apply temperature override if needed
    if model_str in TEMPERATURE_OVERRIDES:
        temperature = TEMPERATURE_OVERRIDES[model_str]

    # Combine the prompt with the text
    full_prompt = f"{prompt}\n\n{text}"

    params = {
        "model": model_str,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    # Handle structured output based on provider capabilities
    if response_format:
        if provider in PROVIDERS_WITH_NATIVE_JSON_SCHEMA:
            # OpenAI supports native json_schema structured output
            params["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": response_format,
                },
            }
        else:
            # For Anthropic, Gemini, etc. - add JSON instruction to prompt
            # These providers don't fully support OpenAI-style json_schema
            # (issues with nullable types, null in enums, etc.)
            schema_str = json.dumps(response_format, indent=2)
            json_instruction = f"""

IMPORTANT: You must respond with valid JSON only. No other text before or after the JSON.
Your response must conform to this JSON schema:
```json
{schema_str}
```

Respond with only the JSON object, no markdown code blocks or explanations."""

            params["messages"][0]["content"] = full_prompt + json_instruction

    response = await litellm.acompletion(**params)
    response_text = response.choices[0].message.content

    # For non-OpenAI providers with response_format, extract JSON from response
    if response_format and provider not in PROVIDERS_WITH_NATIVE_JSON_SCHEMA:
        response_text = extract_json_from_response(response_text)

    if return_usage:
        usage_info = extract_usage_from_response(response, model_str)
        return response_text, usage_info

    return response_text
