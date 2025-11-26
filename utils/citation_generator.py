"""
Citation generation utilities for annotations.

This module provides shared functionality for generating citations
that support extracted annotations by finding relevant quotes in the source text.
"""

import json
from typing import Dict, List

from llm import Model, generate_response


# Single source of truth for citation prompt template
CITATION_PROMPT_TEMPLATE = """You are a research assistant helping extract citations from a scientific article.

Given an annotation about a genetic variant, find the exact sentences or passages in the article that support this annotation. Return 1-3 direct quotes from the article that provide evidence for the annotation.

**Annotation Details:**
- Variant/Haplotype: {variant}
- Gene: {gene}
- Drug: {drug}
- Main Sentence: {sentence}
- Notes: {notes}

**Instructions:**
1. Find sentences in the article that directly support this annotation
2. Return exact quotes from the text (do not paraphrase)
3. Prioritize sentences that mention the variant, gene, and drug together
4. Include surrounding context if needed for clarity
5. Return 1-3 citations maximum

**Article Text:**
{full_text}

Return your response as JSON with a "citations" array containing the exact quote strings.
"""


async def generate_citations(
    annotation: Dict,
    full_text: str,
    model: Model = Model.OPENAI_GPT_4O_MINI,
    citation_prompt_template: str = CITATION_PROMPT_TEMPLATE,
) -> List[str]:
    """
    Generate citations for a single annotation by finding supporting quotes.

    Args:
        annotation: Annotation dictionary with fields like:
            - Variant/Haplotypes
            - Gene
            - Drug(s)
            - Sentence
            - Notes
        full_text: Complete article text to search for citations
        model: LLM model to use for citation generation
        citation_prompt_template: Optional custom prompt template

    Returns:
        List of citation strings (direct quotes from the article)

    Example:
        >>> annotation = {
        ...     "Variant/Haplotypes": "rs1234",
        ...     "Gene": "CYP2D6",
        ...     "Drug(s)": "codeine",
        ...     "Sentence": "Variant affects drug metabolism",
        ...     "Notes": "Poor metabolizer phenotype"
        ... }
        >>> citations = await generate_citations(annotation, article_text)
        >>> print(citations)
        ["Patients with rs1234 showed reduced codeine metabolism...", ...]
    """
    try:
        # Format prompt with annotation details
        formatted_prompt = citation_prompt_template.format(
            variant=annotation.get("Variant/Haplotypes", ""),
            gene=annotation.get("Gene", ""),
            drug=annotation.get("Drug(s)", annotation.get("Drug(s", "")),  # Handle typo
            sentence=annotation.get("Sentence", ""),
            notes=annotation.get("Notes", ""),
            full_text=full_text,
        )

        # Call LLM with JSON output format
        response = await generate_response(
            prompt=formatted_prompt,
            text="",
            model=model,
            response_format={
                "type": "object",
                "properties": {
                    "citations": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
                "required": ["citations"],
            },
        )

        # Parse and return citations
        citations_data = json.loads(response)
        return citations_data.get("citations", [])

    except Exception as e:
        print(f"Error generating citations: {e}")
        return []


async def generate_citations_batch(
    annotations: List[Dict],
    full_text: str,
    model: Model = Model.OPENAI_GPT_4O_MINI,
) -> List[List[str]]:
    """
    Generate citations for multiple annotations in batch.

    Args:
        annotations: List of annotation dictionaries
        full_text: Complete article text
        model: LLM model to use

    Returns:
        List of citation lists, one per annotation
    """
    import asyncio

    tasks = [generate_citations(ann, full_text, model) for ann in annotations]
    return await asyncio.gather(*tasks)
