from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Optional, Sequence

from . import __version__
from .branding import banner_enabled, print_welcome
from .core.append import append_entry
from .core.bootstrap import apply_template_pack, initialize_repository
from .core.context import context_routes
from .core.doctor import run_doctor
from .core.inspection import find_legacy_locations, repository_signals
from .core.models import SetupConfig
from .core.patching import extract_section
from .core.prompts import format_prompt, load_prompts
from .core.resources import (
    export_built_in_templates,
    load_template_pack,
    read_template,
    validate_template_pack,
)
from .core.tasks import refresh_dashboard
from .core.runtime import read_state, set_state_fields
from .hooks import run_hook


def _root(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _print_inspection(root: Path, max_depth: int) -> dict:
    found = find_legacy_locations(root, max_depth=max_depth)
    print(f"Repository: {root}")
    print("\nDetected context locations:")
    for label, key in (
        ("Legacy directories", "legacy_dirs"),
        ("CLAUDE.md files", "claude_files"),
        ("Wiki directories", "wiki_dirs"),
    ):
        values = found[key]
        print(f"  {label}:")
        if values:
            for value in values:
                print(f"    - {value}")
        else:
            print("    - None")
    signals = repository_signals(root)
    print("  Repository signals: " + (", ".join(signals) if signals else "None detected"))
    return found


def _ask_choice(prompt: str, options: Sequence[str], default: int = 1) -> int:
    print(prompt)
    for index, option in enumerate(options, 1):
        print(f"  [{index}] {option}")
    while True:
        raw = input(f"Select [{default}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw)
        print("Please select a valid number.")


def _ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        raw = input(prompt + suffix).strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please answer y or n.")


def _parse_integrations(raw: Iterable[str]) -> tuple[str, ...]:
    values: list[str] = []
    for item in raw:
        for value in item.split(","):
            value = value.strip().lower()
            if value and value not in values:
                values.append(value)
    allowed = {"generic", "claude", "hermes"}
    unknown = [value for value in values if value not in allowed]
    if unknown:
        raise ValueError(f"Unknown integrations: {', '.join(unknown)}")
    return tuple(values)


def _interactive_config(root: Path, force_mode: Optional[str], legacy_found: bool) -> SetupConfig:
    if force_mode:
        mode = force_mode
    else:
        choice = _ask_choice(
            "\nChoose setup mode:",
            [
                "Default — create/repair wiki and update CLAUDE.md",
                "Custom — optional runtime state and repository-local agent integrations",
            ],
            default=1,
        )
        mode = "default" if choice == 1 else "custom"

    if mode == "default":
        return SetupConfig(setup_mode="default")

    runtime_choice = _ask_choice(
        "\nRuntime assistance:",
        [
            "Disabled — wiki only",
            "Assisted — lightweight local resume state",
            "Debug — resume state plus optional scratchpad and logs",
        ],
        default=1,
    )
    runtime_mode = {1: "off", 2: "assisted", 3: "debug"}[runtime_choice]
    scratchpad = runtime_mode == "debug" and _ask_yes_no(
        "Create optional .lliki/scratchpad.md?", default=False
    )

    print("\nRepository-local agent integrations (comma-separated):")
    print("  generic  -> AGENTS.md")
    print("  claude   -> .claude/skills/lliki/")
    print("  hermes   -> .hermes.md")
    raw = input("Select integrations, or leave empty: ").strip()
    integrations = _parse_integrations([raw]) if raw else tuple()
    claude_hooks = False
    if "claude" in integrations:
        claude_hooks = _ask_yes_no(
            "Enable repository-local Claude hooks for mechanical dashboard refresh?",
            default=False,
        )
    legacy_prompt = legacy_found and _ask_yes_no(
        "Also print the optional LLM prompt for reviewing legacy context?",
        default=False,
    )
    return SetupConfig(
        setup_mode="custom",
        runtime_mode=runtime_mode,
        scratchpad=scratchpad,
        integrations=integrations,
        claude_hooks=claude_hooks,
        legacy_prompt=legacy_prompt,
    )


def _noninteractive_config(args: argparse.Namespace) -> SetupConfig:
    integrations = _parse_integrations(args.integrate or [])
    advanced = bool(
        integrations
        or args.runtime != "off"
        or args.scratchpad
        or args.claude_hooks
        or args.legacy_prompt
    )
    if args.default and advanced:
        raise ValueError("Advanced runtime or integration options require --custom")
    setup_mode = "custom" if args.custom or advanced else "default"
    runtime_mode = args.runtime or "off"
    if args.claude_hooks and "claude" not in integrations:
        raise ValueError("--claude-hooks requires --integrate claude")
    return SetupConfig(
        setup_mode=setup_mode,
        runtime_mode=runtime_mode,
        scratchpad=bool(args.scratchpad),
        integrations=integrations,
        claude_hooks=bool(args.claude_hooks),
        legacy_prompt=bool(args.legacy_prompt),
    )


def _show_init_result(data: dict) -> None:
    result = data["result"]
    print("\nPlan result" if data["dry_run"] else "\nSetup result")
    for label, values in (
        ("Created", result.created),
        ("Updated", result.updated),
        ("Preserved", result.preserved),
        ("Backups", result.backups),
        ("Runtime", data["runtime_created"]),
    ):
        if values:
            print(f"  {label}:")
            for value in values:
                print(f"    - {value}")
    if data["integrations"]:
        print("  Integrations:")
        for item in data["integrations"]:
            print(f"    - {item['integration']}: {', '.join(item['files'])}")
    if result.warnings:
        print("  Warnings:")
        for warning in result.warnings:
            print(f"    - {warning}")
    if result.needs_context:
        print("\nFiles requiring LLM or human context:")
        for value in result.needs_context:
            print(f"  - {value}")
    for prompt in data["prompts"]:
        print(prompt)


def command_init(args: argparse.Namespace) -> int:
    root = _root(args.root)
    if args.template_dir:
        os.environ["LLIKI_TEMPLATE_DIR"] = str(_root(args.template_dir))
    interactive = not args.yes and sys.stdin.isatty() and sys.stdout.isatty()
    if interactive and banner_enabled():
        print_welcome()
    found = _print_inspection(root, args.max_depth)
    force_mode = "default" if args.default else "custom" if args.custom else None
    if interactive:
        config = _interactive_config(root, force_mode, bool(found["legacy_dirs"]))
        print("\nSelected configuration:")
        print(f"  Setup: {config.setup_mode}")
        print(f"  Runtime: {config.runtime_mode}")
        print(f"  Scratchpad: {'yes' if config.scratchpad else 'no'}")
        print(f"  Integrations: {', '.join(config.integrations) if config.integrations else 'none'}")
        if not _ask_yes_no("Proceed with this setup?", default=True):
            print("Cancelled.")
            return 1
    else:
        config = _noninteractive_config(args)

    data = initialize_repository(
        root,
        config,
        interactive=interactive,
        yes=args.yes,
        dry_run=args.dry_run,
        max_depth=args.max_depth,
    )
    _show_init_result(data)
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    root = _root(args.root)
    found = find_legacy_locations(root, max_depth=args.max_depth)
    payload = {"root": str(root), "locations": found, "signals": repository_signals(root)}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_inspection(root, args.max_depth)
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    report = run_doctor(_root(args.root))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        summary = report["summary"]
        print(f"Errors: {summary['errors']}  Warnings: {summary['warnings']}")
        for issue in report["issues"]:
            detail = f" ({issue['detail']})" if issue.get("detail") else ""
            print(f"- {issue['severity'].upper()}: {issue['code']}: {issue['path']}{detail}")
    return 0 if report["ok"] else 2


def command_prompt(args: argparse.Namespace) -> int:
    prompts = load_prompts()
    if args.prompt_command == "list":
        for prompt_id, prompt in sorted(prompts.items()):
            print(f"{prompt_id:20} {prompt.title}  total ~{prompt.expected_total_tokens}")
        return 0
    prompt = prompts.get(args.prompt_id)
    if not prompt:
        print(f"Unknown prompt: {args.prompt_id}", file=sys.stderr)
        return 2
    print(format_prompt(prompt))
    return 0


def _template_diff(root: Path) -> list[dict]:
    pack = load_template_pack()
    diffs: list[dict] = []
    for item in pack.files:
        target = root / item.target
        if not target.exists():
            diffs.append({"path": item.target, "status": "missing"})
            continue
        if item.strategy == "managed-section" and item.section_id:
            existing = target.read_text(encoding="utf-8")
            template = read_template(item.template)
            old = extract_section(existing, item.section_id)
            new = extract_section(template, item.section_id)
            if old is None:
                diffs.append({"path": item.target, "status": "unmanaged"})
            elif old != new:
                diffs.append({"path": item.target, "status": "managed-update-available"})
    return diffs


def command_templates(args: argparse.Namespace) -> int:
    if args.templates_command == "export":
        export_built_in_templates(_root(args.destination), force=args.force)
        print(f"Exported editable templates to {_root(args.destination)}")
        return 0
    if args.templates_command == "validate":
        errors = validate_template_pack(_root(args.template_dir) if args.template_dir else None)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 2
        print("Template pack is valid.")
        return 0
    if args.template_dir:
        os.environ["LLIKI_TEMPLATE_DIR"] = str(_root(args.template_dir))
    root = _root(args.root)
    if args.templates_command == "diff":
        diffs = _template_diff(root)
        if args.json:
            print(json.dumps(diffs, indent=2))
        elif not diffs:
            print("No managed template updates or missing files detected.")
        else:
            for item in diffs:
                print(f"{item['status']:28} {item['path']}")
        return 1 if diffs else 0
    if args.templates_command == "sync":
        result = apply_template_pack(
            root,
            interactive=not args.yes and sys.stdin.isatty(),
            yes=args.yes,
            dry_run=args.dry_run,
        )
        print(json.dumps(asdict(result), indent=2) if args.json else _result_text(result))
        return 0
    return 2


def _result_text(result) -> str:
    lines = []
    for label, values in (("Created", result.created), ("Updated", result.updated), ("Preserved", result.preserved)):
        if values:
            lines.append(f"{label}: " + ", ".join(values))
    return "\n".join(lines) or "No changes."


def command_tasks(args: argparse.Namespace) -> int:
    result = refresh_dashboard(
        _root(args.root),
        update_index=args.update_index,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2) if args.json else _mapping_text(result))
    return 0


def _mapping_text(data: dict) -> str:
    return "\n".join(f"{key}: {value}" for key, value in data.items())


def command_context(args: argparse.Namespace) -> int:
    data = context_routes(_root(args.root))
    print(json.dumps(data, indent=2) if args.json else _mapping_text(data))
    return 0



def command_state(args: argparse.Namespace) -> int:
    root = _root(args.root)
    if args.state_command == "show":
        state = read_state(root)
        if not state:
            print("Runtime state is not enabled for this repository.", file=sys.stderr)
            return 2
        print(json.dumps(state, indent=2) if args.json else _mapping_text(state))
        return 0
    blockers = args.blocker if args.blocker is not None else None
    state = set_state_fields(
        root,
        active_task=args.active_task,
        last_result=args.last_result,
        next_action=args.next_action,
        blockers=blockers,
        clear=args.clear,
    )
    print(json.dumps(state, indent=2) if args.json else _mapping_text(state))
    return 0

def command_append(args: argparse.Namespace) -> int:
    content = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    target = append_entry(_root(args.root), args.kind, content)
    print(f"Appended {args.kind} entry to {target}")
    return 0


def command_hook(args: argparse.Namespace) -> int:
    return run_hook(args.event, _root(args.root))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lliki", description="Bootstrap and maintain a local repository wiki.")
    parser.add_argument("--version", action="version", version=f"lliki {__version__}")
    sub = parser.add_subparsers(dest="command")

    init = sub.add_parser("init", help="Create or repair the wiki using the default/custom TUI")
    init.add_argument("--root", default=".")
    modes = init.add_mutually_exclusive_group()
    modes.add_argument("--default", action="store_true", help="Use simple default setup")
    modes.add_argument("--custom", action="store_true", help="Use custom setup")
    init.add_argument("--runtime", choices=["off", "assisted", "debug"], default="off")
    init.add_argument("--scratchpad", action="store_true")
    init.add_argument("--integrate", action="append", help="generic, claude, or hermes; repeatable/comma-separated")
    init.add_argument("--claude-hooks", action="store_true")
    init.add_argument("--legacy-prompt", action="store_true")
    init.add_argument("--template-dir")
    init.add_argument("--dry-run", action="store_true")
    init.add_argument("--yes", "-y", action="store_true")
    init.add_argument("--max-depth", type=int, default=6)
    init.set_defaults(func=command_init)

    inspect = sub.add_parser("inspect", help="Inspect wiki and legacy context locations")
    inspect.add_argument("--root", default=".")
    inspect.add_argument("--max-depth", type=int, default=6)
    inspect.add_argument("--json", action="store_true")
    inspect.set_defaults(func=command_inspect)

    doctor = sub.add_parser("doctor", help="Run token-free structural wiki checks")
    doctor.add_argument("--root", default=".")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=command_doctor)

    prompt = sub.add_parser("prompt", help="Print recommended LLM prompts and token estimates")
    prompt_sub = prompt.add_subparsers(dest="prompt_command", required=True)
    prompt_list = prompt_sub.add_parser("list")
    prompt_list.set_defaults(func=command_prompt)
    prompt_show = prompt_sub.add_parser("show")
    prompt_show.add_argument("prompt_id")
    prompt_show.set_defaults(func=command_prompt)

    templates = sub.add_parser("templates", help="Export, validate, compare, or sync editable templates")
    template_sub = templates.add_subparsers(dest="templates_command", required=True)
    export = template_sub.add_parser("export")
    export.add_argument("destination")
    export.add_argument("--force", action="store_true")
    export.set_defaults(func=command_templates)
    validate = template_sub.add_parser("validate")
    validate.add_argument("--template-dir")
    validate.set_defaults(func=command_templates)
    for name in ("diff", "sync"):
        p = template_sub.add_parser(name)
        p.add_argument("--root", default=".")
        p.add_argument("--template-dir")
        p.add_argument("--json", action="store_true")
        if name == "sync":
            p.add_argument("--dry-run", action="store_true")
            p.add_argument("--yes", "-y", action="store_true")
        p.set_defaults(func=command_templates)

    tasks = sub.add_parser("tasks", help="Mechanical task dashboard operations")
    task_sub = tasks.add_subparsers(dest="tasks_command", required=True)
    refresh = task_sub.add_parser("refresh")
    refresh.add_argument("--root", default=".")
    refresh.add_argument("--update-index", action="store_true")
    refresh.add_argument("--dry-run", action="store_true")
    refresh.add_argument("--json", action="store_true")
    refresh.set_defaults(func=command_tasks)

    context = sub.add_parser("context", help="Return bounded context routes without reading full content")
    context.add_argument("--root", default=".")
    context.add_argument("--json", action="store_true")
    context.set_defaults(func=command_context)


    state = sub.add_parser("state", help="Agent-facing lightweight resume-state operations")
    state_sub = state.add_subparsers(dest="state_command", required=True)
    state_show = state_sub.add_parser("show")
    state_show.add_argument("--root", default=".")
    state_show.add_argument("--json", action="store_true")
    state_show.set_defaults(func=command_state)
    state_update = state_sub.add_parser("update")
    state_update.add_argument("--root", default=".")
    state_update.add_argument("--active-task")
    state_update.add_argument("--last-result")
    state_update.add_argument("--next-action")
    state_update.add_argument("--blocker", action="append")
    state_update.add_argument("--clear", action="store_true")
    state_update.add_argument("--json", action="store_true")
    state_update.set_defaults(func=command_state)

    append = sub.add_parser("append", help="Safely append a decision or lesson entry")
    append.add_argument("kind", choices=["decision", "lesson"])
    append.add_argument("--root", default=".")
    append.add_argument("--file", help="Read entry from file; otherwise stdin")
    append.set_defaults(func=command_append)

    hook = sub.add_parser("hook", help="Internal repository-integration lifecycle hook")
    hook.add_argument("event", choices=["claude-session-start", "claude-task-completed", "claude-stop"])
    hook.add_argument("--root", default=".")
    hook.set_defaults(func=command_hook)
    return parser


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv: Optional[Sequence[str]] = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        args = parser.parse_args(["init"] + list(argv or []))
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130
    except (ValueError, FileNotFoundError, PermissionError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
