from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

from .models import PromptTemplate
from .resources import iter_template_paths, read_template

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


def _parse_metadata(raw: str) -> tuple[Dict[str, str], str]:
    match = _FRONTMATTER.match(raw)
    if not match:
        raise ValueError("Prompt template is missing front matter")
    metadata: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, match.group(2).strip() + "\n"


def load_prompts() -> Dict[str, PromptTemplate]:
    prompts: Dict[str, PromptTemplate] = {}
    for path in iter_template_paths("prompts"):
        raw = read_template(path)
        metadata, body = _parse_metadata(raw)
        prompt_id = metadata.get("id") or Path(path).stem
        prompts[prompt_id] = PromptTemplate(
            prompt_id=prompt_id,
            title=metadata.get("title", prompt_id),
            expected_total_tokens=metadata.get("expected_total_tokens", "unknown"),
            body=body,
            source=Path(path),
        )
    return prompts


def estimate_prompt_tokens(text: str) -> int:
    # Conservative model-neutral estimate for English/code-heavy Markdown.
    by_chars = (len(text) + 3) // 4
    by_words = int(len(text.split()) * 1.35)
    return max(by_chars, by_words)


def format_prompt(prompt: PromptTemplate) -> str:
    estimate = estimate_prompt_tokens(prompt.body)
    line = "─" * 64
    return (
        f"\n{prompt.title}\n{line}\n{prompt.body}{line}\n"
        f"Estimated LLM usage:\n"
        f"  Prompt only: ~{estimate} tokens\n"
        f"  Expected total call: ~{prompt.expected_total_tokens} tokens\n"
        "  Actual usage depends on the model and repository context loaded.\n"
    )
