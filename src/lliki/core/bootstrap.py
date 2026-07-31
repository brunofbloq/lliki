from __future__ import annotations

from pathlib import Path
from typing import Callable

from lliki.integrations.install import install_selected

from .inspection import find_legacy_locations, repository_signals
from .models import OperationResult, SetupConfig, TemplateFile
from .patching import append_section, atomic_write, backup_file, replace_section
from .prompts import format_prompt, load_prompts
from .resources import load_template_pack, read_template
from .runtime import ensure_gitignore, write_runtime_config

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]


def _ask_yes_no(prompt: str, default: bool, input_fn: InputFn, output_fn: OutputFn) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        value = input_fn(prompt + suffix).strip().lower()
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        output_fn("Please answer y or n.")


def _handle_existing_managed(
    root: Path,
    item: TemplateFile,
    template: str,
    interactive: bool,
    yes: bool,
    input_fn: InputFn,
    output_fn: OutputFn,
    result: OperationResult,
    dry_run: bool,
) -> None:
    path = root / item.target
    existing = path.read_text(encoding="utf-8")
    assert item.section_id
    updated, changed = replace_section(existing, template, item.section_id)
    if changed:
        proceed = yes or not interactive or _ask_yes_no(
            f"Update managed section in {item.target}?", True, input_fn, output_fn
        )
        if proceed:
            if not dry_run:
                backup = backup_file(path)
                result.backups.append(backup.relative_to(root).as_posix())
                atomic_write(path, updated)
            result.updated.append(item.target)
        else:
            result.preserved.append(item.target)
        return

    if f"id={item.section_id}" in existing:
        result.preserved.append(item.target)
        return

    # The default setup must safely update CLAUDE.md. Other unmarked managed
    # files are preserved to avoid duplicating an existing document.
    if item.target == "CLAUDE.md":
        proceed = yes or not interactive or _ask_yes_no(
            "Existing CLAUDE.md has no lliki section. Append the stable managed contract?",
            True,
            input_fn,
            output_fn,
        )
        if proceed:
            appended = append_section(existing, template, item.section_id)
            if not dry_run:
                backup = backup_file(path)
                result.backups.append(backup.relative_to(root).as_posix())
                atomic_write(path, appended)
            result.updated.append(item.target)
        else:
            result.preserved.append(item.target)
    else:
        result.preserved.append(item.target)
        result.warnings.append(
            f"Preserved unmarked managed file {item.target}; run templates sync with review to adopt managed sections."
        )


def apply_template_pack(
    root: Path,
    *,
    interactive: bool = True,
    yes: bool = False,
    dry_run: bool = False,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
) -> OperationResult:
    pack = load_template_pack()
    result = OperationResult()
    for directory in pack.directories:
        path = root / directory
        if not path.exists():
            if not dry_run:
                path.mkdir(parents=True, exist_ok=True)
            result.created.append(directory + "/")

    for item in pack.files:
        target = root / item.target
        template = read_template(item.template)
        if not target.exists():
            if not dry_run:
                atomic_write(target, template)
            result.created.append(item.target)
            if item.needs_context:
                result.needs_context.append(item.target)
            continue

        if item.strategy == "managed-section":
            _handle_existing_managed(
                root, item, template, interactive, yes, input_fn, output_fn, result, dry_run
            )
        else:
            result.preserved.append(item.target)
            if item.needs_context:
                text = target.read_text(encoding="utf-8")
                if "NEEDS_CONTEXT: LLM_OR_HUMAN" in text or "Needs validation" in text:
                    result.needs_context.append(item.target)
    return result


def initialize_repository(
    root: Path,
    config: SetupConfig,
    *,
    interactive: bool = True,
    yes: bool = False,
    dry_run: bool = False,
    max_depth: int = 6,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
) -> dict:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    inspection = find_legacy_locations(root, max_depth=max_depth)
    signals = repository_signals(root)
    result = apply_template_pack(
        root,
        interactive=interactive,
        yes=yes,
        dry_run=dry_run,
        input_fn=input_fn,
        output_fn=output_fn,
    )

    integration_results = []
    runtime_created: list[str] = []
    if not dry_run and config.integrations:
        integration_results = install_selected(root, config.integrations, config.claude_hooks)

    if not dry_run and config.runtime_mode != "off":
        runtime_created = write_runtime_config(
            root,
            mode=config.runtime_mode,
            integrations=list(config.integrations),
            scratchpad=config.scratchpad,
            hooks=config.claude_hooks,
        )
        if ensure_gitignore(root):
            runtime_created.append(".gitignore")

    prompts = load_prompts()
    prompt_outputs = [format_prompt(prompts["initialize-project"])]
    if config.legacy_prompt and inspection["legacy_dirs"]:
        prompt_outputs.append(format_prompt(prompts["migrate-legacy"]))

    return {
        "root": str(root),
        "config": config,
        "inspection": inspection,
        "signals": signals,
        "result": result,
        "integrations": integration_results,
        "runtime_created": runtime_created,
        "prompts": prompt_outputs,
        "dry_run": dry_run,
    }
