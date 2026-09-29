from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Optional, Sequence

from . import __version__
from .branding import banner_enabled, print_welcome, render_commands_panel
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
from .core.documents import create_document
from .core.indexing import refresh_indexes
from .core.notes import append_to_note, list_notes, new_note, search_notes, show_note
from .core.update import run_update
from .core.updatecheck import force_check, update_notice
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
                "Custom — repository-local agent integrations",
            ],
            default=1,
        )
        mode = "default" if choice == 1 else "custom"

    if mode == "default":
        return SetupConfig(setup_mode="default")

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
        integrations=integrations,
        claude_hooks=claude_hooks,
        legacy_prompt=legacy_prompt,
    )


def _noninteractive_config(args: argparse.Namespace) -> SetupConfig:
    integrations = _parse_integrations(args.integrate or [])
    advanced = bool(
        integrations
        or args.claude_hooks
        or args.legacy_prompt
    )
    if args.default and advanced:
        raise ValueError("Advanced integration options require --custom")
    setup_mode = "custom" if args.custom or advanced else "default"
    if args.claude_hooks and "claude" not in integrations:
        raise ValueError("--claude-hooks requires --integrate claude")
    return SetupConfig(
        setup_mode=setup_mode,
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
    ):
        if values:
            print(f"  {label}:")
            for value in values:
                print(f"    - {value}")
    if data["integrations"]:
        print("  Integrations:")
        for item in data["integrations"]:
            if item.get("message"):
                print("    " + item["message"].replace("\n", "\n    "))
            else:
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
        #print("\nSelected configuration:")
        #print(f"  Setup: {config.setup_mode}")
        #print(f"  Integrations: {', '.join(config.integrations) if config.integrations else 'none'}")
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


def command_doctor(args: argparse.Namespace) -> int:
    root = _root(args.root)
    report = run_doctor(root)
    inspection = find_legacy_locations(root, max_depth=args.max_depth)
    signals = repository_signals(root)
    if args.json:
        report["inspection"] = {"locations": inspection, "signals": signals}
        print(json.dumps(report, indent=2))
    else:
        summary = report["summary"]
        print(f"Errors: {summary['errors']}  Warnings: {summary['warnings']}")
        for issue in report["issues"]:
            detail = f" ({issue['detail']})" if issue.get("detail") else ""
            print(f"- {issue['severity'].upper()}: {issue['code']}: {issue['path']}{detail}")
        if inspection["legacy_dirs"]:
            print("Legacy locations:")
            for value in inspection["legacy_dirs"]:
                print(f"- {value}")
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
    if getattr(args, "tasks_command", None) == "new":
        result = create_document(_root(args.root), "task", args.title, tags=args.tags)
        print(f"Created {result['path']} (id {result['id']}); wiki/tasks/tasks-index.md refreshed.")
        return 0
    result = refresh_indexes(_root(args.root), ["tasks"], dry_run=args.dry_run)
    print(json.dumps(result, indent=2) if args.json else _mapping_text(result))
    return 0


def command_index(args: argparse.Namespace) -> int:
    folders = None if args.all else ([args.folder] if args.folder else None)
    result = refresh_indexes(_root(args.root), folders)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for bucket in ("created", "refreshed", "unchanged"):
            if result[bucket]:
                print(f"{bucket}: " + ", ".join(result[bucket]))
        for warning in result["warnings"]:
            print(f"WARNING: {warning}", file=sys.stderr)
    return 1 if result["warnings"] else 0


def command_explore(args: argparse.Namespace) -> int:
    result = create_document(_root(args.root), "exploratory", args.title, tags=args.tags)
    print(f"Created {result['path']}; wiki/exploratory/exploratory-index.md refreshed.")
    return 0


def command_notes(args: argparse.Namespace) -> int:
    root = _root(args.root)
    if args.notes_command == "new":
        result = new_note(root, args.title, tags=args.tags)
        print(f"Created {result['path']}; {result['index_refreshed']} index refreshed.")
        return 0
    if args.notes_command == "list":
        entries = list_notes(root)
        if args.json:
            print(json.dumps(entries, indent=2))
        else:
            for entry in entries:
                print(f"{entry['path']}  {entry['title']}")
            if not entries:
                print("No notes.")
        return 0
    if args.notes_command == "show":
        print(show_note(root, args.name))
        return 0
    if args.notes_command == "append":
        content = sys.stdin.read() if args.file in {None, "-"} else Path(args.file).read_text(encoding="utf-8")
        path = append_to_note(root, args.name, content, heading=args.heading)
        print(f"Appended to {path}")
        return 0
    if args.notes_command == "search":
        results = search_notes(root, args.term)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for item in results:
                print(item["path"])
                for line in item["matches"]:
                    print(f"  {line}")
            if not results:
                print(f"No matches for: {args.term}")
        return 0
    return 2


def command_integration(args: argparse.Namespace) -> int:
    root = _root(args.root)
    markers = {
        "generic": ("AGENTS.md", "generic-agent-contract"),
        "claude": (".claude/skills/lliki/SKILL.md", "claude-lliki-skill"),
        "hermes": (".hermes.md", "hermes-agent-contract"),
    }
    status = {}
    for name, (target, section) in markers.items():
        path = root / target
        if not path.exists():
            status[name] = "not installed"
        elif section in path.read_text(encoding="utf-8"):
            status[name] = "installed (managed section present)"
        else:
            status[name] = "installed (unmanaged file)"
    print(json.dumps(status, indent=2) if args.json else "\n".join(f"{k}: {v}" for k, v in status.items()))
    return 0


def command_version(args: argparse.Namespace) -> int:
    if args.check:
        payload = force_check(__version__)
        if args.json:
            print(json.dumps(payload, indent=2))
            return 0
        if not payload["ok"]:
            print(f"Update check failed: {payload['detail']}", file=sys.stderr)
            return 1
        if payload["update_available"]:
            print(f"lliki {payload['current']} is installed; {payload['latest']} is available. Run: pip install -U lliki")
        else:
            print(f"lliki {payload['current']} is up to date.")
        return 0
    print(f"lliki {__version__}")
    return 0


def _mapping_text(data: dict) -> str:
    return "\n".join(f"{key}: {value}" for key, value in data.items())


def command_context(args: argparse.Namespace) -> int:
    data = context_routes(_root(args.root))
    print(json.dumps(data, indent=2) if args.json else _mapping_text(data))
    return 0


def _show_update_result(data: dict) -> None:
    print("Update result" if not data["dry_run"] else "Update plan")
    actions = data["actions"]
    for label, values in (
        ("Created", actions["created"]),
        ("Updated", actions["updated"]),
        ("Preserved", actions["preserved"]),
        ("Backups", actions["backups"]),
    ):
        if values:
            print(f"  {label}:")
            for value in values:
                print(f"    - {value}")
    migrated = data["actions"].get("migrated") or []
    if migrated:
        print("  Migration:")
        for action in migrated:
            print(f"    - {action}")
    indexes = data["indexes"]
    if indexes["created"] or indexes["refreshed"]:
        print("  Indexes:")
        print(f"    - created: {', '.join(indexes['created']) or 'none'}")
        print(f"    - refreshed: {', '.join(indexes['refreshed']) or 'none'}")
    doctor = data["doctor"]["summary"]
    print("  Doctor:")
    print(f"    - errors: {doctor['errors']}")
    print(f"    - warnings: {doctor['warnings']}")
    if data["warnings"]:
        print("  Warnings:")
        for warning in data["warnings"]:
            print(f"    - {warning}")
    if data["semantic_migration_needed"]:
        print("\nSemantic migration needed. Suggested prompt:")
        print(data["migration_prompt"])
    else:
        print("\nNext action: run `lliki doctor` or continue normal work.")


def command_update(args: argparse.Namespace) -> int:
    data = run_update(_root(args.root), dry_run=args.dry_run, max_depth=args.max_depth)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        _show_update_result(data)
    return 0 if data["doctor"]["ok"] else 2



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
    init.add_argument("--integrate", action="append", help="generic, claude, or hermes; repeatable/comma-separated")
    init.add_argument("--claude-hooks", action="store_true")
    init.add_argument("--legacy-prompt", action="store_true")
    init.add_argument("--template-dir")
    init.add_argument("--dry-run", action="store_true")
    init.add_argument("--yes", "-y", action="store_true")
    init.add_argument("--max-depth", type=int, default=6)
    init.set_defaults(func=command_init)

    doctor = sub.add_parser("doctor", help="Structural wiki health checks plus legacy-location inspection")
    doctor.add_argument("--root", default=".")
    doctor.add_argument("--max-depth", type=int, default=6)
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

    tasks = sub.add_parser("tasks", aliases=["task"], help="Refresh tasks-index; 'tasks new' creates a task")
    task_sub = tasks.add_subparsers(dest="tasks_command")
    task_new = task_sub.add_parser("new", help="Create a task document from the task template")
    task_new.add_argument("title")
    task_new.add_argument("--root", default=".")
    task_new.add_argument("--tag", dest="tags", action="append")
    task_new.set_defaults(func=command_tasks)
    tasks.set_defaults(func=command_tasks)
    tasks.add_argument("--root", default=".")
    tasks.add_argument("--dry-run", action="store_true")
    tasks.add_argument("--json", action="store_true")

    notes = sub.add_parser("notes", help="Notes workflow over wiki/notes")
    notes_sub = notes.add_subparsers(dest="notes_command", required=True)
    notes_new = notes_sub.add_parser("new")
    notes_new.add_argument("title")
    notes_new.add_argument("--root", default=".")
    notes_new.add_argument("--tag", dest="tags", action="append")
    notes_new.set_defaults(func=command_notes)
    notes_list = notes_sub.add_parser("list")
    notes_list.add_argument("--root", default=".")
    notes_list.add_argument("--json", action="store_true")
    notes_list.set_defaults(func=command_notes)
    notes_show = notes_sub.add_parser("show")
    notes_show.add_argument("name")
    notes_show.add_argument("--root", default=".")
    notes_show.set_defaults(func=command_notes)
    notes_append = notes_sub.add_parser("append")
    notes_append.add_argument("name")
    notes_append.add_argument("--file")
    notes_append.add_argument("--heading")
    notes_append.add_argument("--root", default=".")
    notes_append.set_defaults(func=command_notes)
    notes_search = notes_sub.add_parser("search")
    notes_search.add_argument("term")
    notes_search.add_argument("--root", default=".")
    notes_search.add_argument("--json", action="store_true")
    notes_search.set_defaults(func=command_notes)

    explore = sub.add_parser("explore", help="Exploratory work documents")
    explore_sub = explore.add_subparsers(dest="explore_command", required=True)
    explore_new = explore_sub.add_parser("new")
    explore_new.add_argument("title")
    explore_new.add_argument("--root", default=".")
    explore_new.add_argument("--tag", dest="tags", action="append")
    explore_new.set_defaults(func=command_explore)

    index = sub.add_parser("index", help="Refresh named folder indexes")
    index.add_argument("folder", nargs="?", help="wiki subfolder name; omit for all")
    index.add_argument("--all", action="store_true")
    index.add_argument("--root", default=".")
    index.add_argument("--json", action="store_true")
    index.set_defaults(func=command_index)

    integration = sub.add_parser("integration", help="Repository-local agent integration management")
    integration.add_argument("--root", default=".")
    integration.add_argument("--json", action="store_true")
    integration_sub = integration.add_subparsers(dest="integration_command")
    integration_status = integration_sub.add_parser("status")
    integration_status.add_argument("--root", default=".")
    integration_status.add_argument("--json", action="store_true")
    integration_status.set_defaults(func=command_integration)
    integration_hook = integration_sub.add_parser("hook", help="Internal lifecycle hook invoked by agent settings")
    integration_hook.add_argument("event", choices=["claude-session-start", "claude-task-completed", "claude-stop"])
    integration_hook.add_argument("--root", default=".")
    integration_hook.set_defaults(func=command_hook)
    integration.set_defaults(func=command_integration)

    version = sub.add_parser("version", help="Print the installed version, or check PyPI")
    version.add_argument("--check", action="store_true")
    version.add_argument("--json", action="store_true")
    version.set_defaults(func=command_version)

    context = sub.add_parser("context", help="Show agent routing state: entry, active task, folder indexes")
    context.add_argument("--root", default=".")
    context.add_argument("--json", action="store_true")
    context.set_defaults(func=command_context)

    update = sub.add_parser("update", help="Safely update an existing wiki to the installed Lliki model")
    update.add_argument("--root", default=".")
    update.add_argument("--dry-run", action="store_true")
    update.add_argument("--json", action="store_true")
    update.add_argument("--max-depth", type=int, default=6)
    update.set_defaults(func=command_update)


    append = sub.add_parser("append", help="Append a decision or lesson entry, preserving existing content")
    append.add_argument("kind", choices=["decision", "lesson"])
    append.add_argument("--root", default=".")
    append.add_argument("--file", help="Read entry from file; otherwise stdin")
    append.set_defaults(func=command_append)
    return parser


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def _command_helps(parser: argparse.ArgumentParser) -> dict:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return {a.dest: a.help or "" for a in action._choices_actions}
    return {}


_COMMON_COMMANDS = ("init", "update", "doctor", "index", "tasks", "context", "prompt")


def main(argv: Optional[Sequence[str]] = None) -> int:
    _configure_stdio()
    argv = list(argv) if argv is not None else None
    if argv and argv[:1] == ["hook"]:  # alias kept for installed agent settings
        argv = ["integration", "hook"] + argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command not in {"version", "init", "update", "doctor"} and sys.stdout.isatty():
        try:
            notice = update_notice(__version__)
            if notice:
                print(f"NOTE: {notice}", file=sys.stderr)
        except Exception:
            pass
    if not args.command:
        print_welcome()
        helps = _command_helps(parser)
        print(render_commands_panel([(name, helps.get(name, "")) for name in _COMMON_COMMANDS]))
        print("\nRun `lliki --help` for all commands; setup runs via `lliki init`.")
        return 0
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130
    except (ValueError, FileNotFoundError, PermissionError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
