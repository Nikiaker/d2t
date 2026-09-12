"""Prompt shared by fine-tuning and joint inference."""

import json
from typing import Any


SYSTEM_PROMPT = (
    "You convert one structured data instance into concise natural language and a "
    "corresponding set of RDF semantic triples. "
    'Return ONLY JSON with schema: {"text":"...","triples":[{'
    '"subject":"...","predicate":"...","object":"..."}]}. '
    "Capture the most important information, trends, extremes, and notable conditions. "
    "Use concise predicate labels in lower_snake_case when possible and avoid duplicates. "
    "If the instance contains a time series (for example a weather forecast), summarize it "
    "at a high level instead of listing every point."
)


def build_user_prompt(instance: dict[str, Any]) -> str:
    """Build the byte-stable user prompt used during fine-tuning."""
    return (
        "Create a concise natural-language summary of this ONE data instance "
        "and extract its semantic triples.\n\n"
        f"instance_context={json.dumps(instance, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
