from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple


@dataclass(frozen=True)
class TemplateFile:
    template: str
    target: str
    strategy: str
    section_id: Optional[str] = None
    needs_context: bool = False


@dataclass(frozen=True)
class TemplatePack:
    schema_version: int
    version: str
    directories: Tuple[str, ...]
    files: Tuple[TemplateFile, ...]


@dataclass
class SetupConfig:
    setup_mode: str = "default"
    integrations: Tuple[str, ...] = field(default_factory=tuple)
    claude_hooks: bool = False
    legacy_prompt: bool = False


@dataclass
class OperationResult:
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    preserved: list[str] = field(default_factory=list)
    backups: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    needs_context: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PromptTemplate:
    prompt_id: str
    title: str
    expected_total_tokens: str
    body: str
    source: Path
