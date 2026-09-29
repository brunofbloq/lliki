from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from lliki.cli import main
from lliki.branding import AUTHOR, banner_enabled, render_welcome
from lliki.core.bootstrap import initialize_repository
from lliki.core.context import context_routes
from lliki.core.doctor import run_doctor
from lliki.core.models import SetupConfig
from lliki.core.prompts import estimate_prompt_tokens, load_prompts
from lliki.core.resources import export_built_in_templates, validate_template_pack
from lliki.core.update import run_update
from lliki.hooks import run_hook


class LlikiTests(unittest.TestCase):

    def test_welcome_banner_contains_branding_and_compact_fallback(self):
        large = render_welcome(100)
        compact = render_welcome(60)
        self.assertIn("Local-first repository wiki", large)
        self.assertIn("_       _", compact)
        self.assertEqual(AUTHOR, "brunofbloq")

    def test_banner_can_be_disabled_with_environment_variable(self):
        old = os.environ.get("LLIKI_NO_BANNER")
        os.environ["LLIKI_NO_BANNER"] = "1"
        try:
            self.assertFalse(banner_enabled())
        finally:
            if old is None:
                os.environ.pop("LLIKI_NO_BANNER", None)
            else:
                os.environ["LLIKI_NO_BANNER"] = old

    def test_default_setup_creates_minimal_wiki_without_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            self.assertTrue((root / "CLAUDE.md").exists())
            self.assertTrue((root / "wiki/wiki-index.md").exists())
            self.assertFalse((root / "wiki/index.md").exists())
            self.assertTrue((root / "wiki/tasks/scratchpad.md").exists())
            for index in ("wiki/docs/docs-index.md", "wiki/tasks/tasks-index.md",
                          "wiki/exploratory/exploratory-index.md", "wiki/notes/notes-index.md"):
                self.assertTrue((root / index).exists(), index)
            self.assertFalse((root / "wiki/tasks/resume.md").exists())
            self.assertIn("/wiki/tasks/scratchpad.md", (root / ".gitignore").read_text(encoding="utf-8"))
            self.assertIn("/wiki/tasks/.backup/", (root / ".gitignore").read_text(encoding="utf-8"))
            self.assertFalse((root / ".lliki").exists())
            self.assertNotIn("embedded-systems-architect", data["prompts"][0])
            self.assertNotIn("embedded-systems-architect", (root / "CLAUDE.md").read_text())

    def test_existing_claude_is_preserved_and_managed_contract_appended_once(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = "# Existing rules\n\nKeep this line.\n"
            (root / "CLAUDE.md").write_text(original, encoding="utf-8")
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            text = (root / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("Keep this line.", text)
            self.assertEqual(text.count("lliki:managed:start id=lliki-contract"), 1)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            text2 = (root / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertEqual(text2.count("lliki:managed:start id=lliki-contract"), 1)

    def test_custom_setup_uses_shared_scratchpad_and_no_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = SetupConfig(
                setup_mode="custom",
                integrations=("generic", "claude", "hermes"),
                claude_hooks=True,
            )
            initialize_repository(root, config, interactive=False, yes=True)
            self.assertFalse((root / ".lliki").exists())
            self.assertTrue((root / "wiki/tasks/scratchpad.md").exists())
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertTrue((root / ".hermes.md").exists())
            settings = json.loads((root / ".claude/settings.json").read_text())
            self.assertIn("SessionStart", settings["hooks"])
            self.assertIn("/wiki/tasks/scratchpad.md", (root / ".gitignore").read_text())
            for path in ("AGENTS.md", ".hermes.md", ".claude/skills/lliki/SKILL.md"):
                self.assertNotIn(".lliki", (root / path).read_text(encoding="utf-8"))

    def test_prompt_metadata_and_estimates(self):
        prompts = load_prompts()
        self.assertIn("initialize-project", prompts)
        prompt = prompts["initialize-project"]
        self.assertGreater(estimate_prompt_tokens(prompt.body), 100)
        self.assertEqual(prompt.expected_total_tokens, "3000-7000")

    def test_tasks_index_routes_scratchpad_current_task(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            (root / "wiki/tasks/scratchpad.md").write_text(
                "---\nid: LOCAL\ntitle: Local scratchpad\nstatus: active\n---\n# Not a task\n",
                encoding="utf-8",
            )
            task = root / "wiki/tasks/HWRD-115-sensor.md"
            task.write_text(
                "---\nid: HWRD-115\ntitle: Sensor bring-up\nstatus: active\npriority: high\nupdated: 2026-07-31\n---\n# Task\n",
                encoding="utf-8",
            )
            from lliki.core.indexing import refresh_indexes
            refresh_indexes(root, ["tasks"])
            dashboard = (root / "wiki/tasks/tasks-index.md").read_text()
            self.assertIn("HWRD-115", dashboard)
            self.assertNotIn("Recently Completed", dashboard)
            self.assertNotIn("HWRD-115", (root / "wiki/wiki-index.md").read_text())
            current = dashboard.split("## Current Task", 1)[1]
            self.assertIn("- None.", current)  # inactive scratchpad keeps route None
            self.assertFalse((root / "wiki/tasks/resume.md").exists())
            # active scratchpad drives the generated Current Task region
            (root / "wiki/tasks/scratchpad.md").write_text(
                "# S\n\n## Task\n\n- **File:** `wiki/tasks/HWRD-115-sensor.md`\n\n## Next Action\n\nGo.\n",
                encoding="utf-8",
            )
            refresh_indexes(root, ["tasks"])
            dashboard = (root / "wiki/tasks/tasks-index.md").read_text()
            current = dashboard.split("## Current Task", 1)[1]
            self.assertIn("HWRD-115", current)
            self.assertIn("scratchpad", current)

    def test_tasks_index_links_closed_tasks_without_routing_them_as_current(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            for task_id, status in (("LLIKI-900", "done"), ("LLIKI-902", "completed"), ("LLIKI-903", "cancelled")):
                (root / f"wiki/tasks/{task_id.lower()}-{status}.md").write_text(
                    f"---\nid: {task_id}\ntitle: Finished task\nstatus: {status}\n---\n# Task\n",
                    encoding="utf-8",
                )
            planned = root / "wiki/tasks/LLIKI-901-planned.md"
            planned.write_text(
                "---\nid: LLIKI-901\ntitle: Upcoming task\nstatus: planned\n---\n# Task\n",
                encoding="utf-8",
            )
            from lliki.core.indexing import refresh_indexes
            refresh_indexes(root, ["tasks"])
            index = (root / "wiki/tasks/tasks-index.md").read_text(encoding="utf-8")
            planned_section, closed_section = index.split("## Planned", 1)[1].split("## Closed", 1)
            self.assertIn("LLIKI-901", planned_section)
            for task_id in ("LLIKI-900", "LLIKI-902", "LLIKI-903"):
                self.assertNotIn(task_id, planned_section)
                self.assertIn(task_id, closed_section)
                self.assertEqual(index.count(f"|{task_id}]]"), 1)
            self.assertIn("- None.", index.split("## Current Task", 1)[1])
            self.assertFalse((root / "wiki/tasks/resume.md").exists())
            self.assertFalse(any(issue["code"] == "WIKI003-orphan-document" for issue in run_doctor(root)["issues"]))

    def test_task_index_backups_are_kept_in_backup_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            (root / "wiki/tasks/HWRD-115-sensor.md").write_text(
                "---\nid: HWRD-115\ntitle: Sensor bring-up\nstatus: active\npriority: high\n---\n# Task\n",
                encoding="utf-8",
            )
            from lliki.core.indexing import refresh_indexes
            refresh_indexes(root, ["tasks"])
            self.assertTrue(list((root / "wiki/tasks/.backup").glob("tasks-index.md.bak.*")))
            self.assertEqual(list((root / "wiki/tasks").glob("*.md.bak.*")), [])

    def test_layout_migration_retires_resume_and_moves_existing_backups(self):
        from lliki.core.migration import migrate_legacy_layout
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            (root / "wiki/tasks/resume.md").write_text("# Resume\n", encoding="utf-8")
            old_backup = root / "wiki/tasks/dashboard.md.bak.old"
            old_backup.write_text("old backup\n", encoding="utf-8")
            actions = migrate_legacy_layout(root)
            self.assertFalse((root / "wiki/tasks/resume.md").exists())
            self.assertEqual((root / "wiki/tasks/.backup/resume.md").read_text(encoding="utf-8"), "# Resume\n")
            self.assertFalse(old_backup.exists())
            self.assertEqual((root / "wiki/tasks/.backup/dashboard.md.bak.old").read_text(encoding="utf-8"), "old backup\n")
            self.assertTrue(any("resume.md" in action for action in actions))
            # idempotent
            self.assertEqual([a for a in migrate_legacy_layout(root) if "resume" in a], [])

    def test_layout_migration_dry_run_touches_nothing(self):
        from lliki.core.migration import migrate_legacy_layout
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            (root / "wiki/tasks/resume.md").write_text("# Resume\n", encoding="utf-8")
            old_backup = root / "wiki/tasks/dashboard.md.bak.old"
            old_backup.write_text("old backup\n", encoding="utf-8")
            migrate_legacy_layout(root, dry_run=True)
            self.assertTrue((root / "wiki/tasks/resume.md").exists())
            self.assertTrue(old_backup.exists())
            self.assertFalse((root / "wiki/tasks/.backup/dashboard.md.bak.old").exists())

    def test_template_export_and_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "templates"
            export_built_in_templates(destination)
            self.assertTrue((destination / "CLAUDE.md").exists())
            self.assertEqual(validate_template_pack(destination), [])

    def test_docs_prefer_scratchpad_progress_and_concise_task_completion(self):
        root = Path(__file__).resolve().parents[1]
        rules = (root / "src/lliki/templates/wiki/wiki-rules.md").read_text(encoding="utf-8")
        prompt = (root / "src/lliki/templates/prompts/complete-task.md").read_text(encoding="utf-8")
        self.assertIn("Do not check off acceptance criteria step by step", rules)
        self.assertIn("concise final result and validation summary", prompt)
        self.assertIn("Do not copy scratchpad history or long evidence dumps", prompt)

    def test_custom_template_can_update_only_managed_claude_section(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "repo"
            templates = base / "templates"
            root.mkdir()
            export_built_in_templates(templates)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            claude_template = templates / "CLAUDE.md"
            claude_template.write_text(
                claude_template.read_text().replace(
                    "This file defines stable repository-wide behavior",
                    "This file defines TEST repository-wide behavior",
                ),
                encoding="utf-8",
            )
            old = os.environ.get("LLIKI_TEMPLATE_DIR")
            os.environ["LLIKI_TEMPLATE_DIR"] = str(templates)
            try:
                initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            finally:
                if old is None:
                    os.environ.pop("LLIKI_TEMPLATE_DIR", None)
                else:
                    os.environ["LLIKI_TEMPLATE_DIR"] = old
            self.assertIn(
                "TEST repository-wide behavior",
                (root / "CLAUDE.md").read_text(encoding="utf-8"),
            )

    def test_doctor_ignores_example_links_in_comments(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            report = run_doctor(root)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertNotIn("scratchpad-not-ignored", codes)
            self.assertNotIn("task-backups-not-ignored", codes)
            broken = [i for i in report["issues"] if i["code"] == "broken-wiki-link"]
            self.assertEqual(broken, [])

    def test_doctor_ignores_task_backup_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            backup_dir = root / "wiki/tasks/.backup"
            backup_dir.mkdir()
            (backup_dir / "noisy.md").write_text("[[missing-page]]\n", encoding="utf-8")
            report = run_doctor(root)
            self.assertNotIn("broken-wiki-link", {issue["code"] for issue in report["issues"]})

    def test_legacy_inspection_does_not_report_wiki_tasks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            from lliki.core.inspection import find_legacy_locations
            found = find_legacy_locations(root)
            self.assertNotIn("wiki/tasks", found["legacy_dirs"])

    def test_removed_deprecated_commands_are_rejected(self):
        for argv in (["state", "show"], ["inspect"], ["init", "--scratchpad"], ["init", "--runtime", "assisted"]):
            with tempfile.TemporaryDirectory() as temp:
                stderr = io.StringIO()
                with redirect_stderr(stderr):
                    with self.assertRaises(SystemExit):
                        main(argv + ["--root", temp])
                self.assertIn("usage:", stderr.getvalue())

    def test_doctor_includes_legacy_inspection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            (root / ".context").mkdir()
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["doctor", "--root", str(root), "--json"])
            payload = json.loads(output.getvalue())
            self.assertIn("legacy_dirs", payload["inspection"]["locations"])
            self.assertIn(".context", payload["inspection"]["locations"]["legacy_dirs"])
            self.assertIn("signals", payload["inspection"])
            text_out = io.StringIO()
            with redirect_stdout(text_out):
                main(["doctor", "--root", str(root)])
            self.assertIn("Legacy locations:", text_out.getvalue())

    def test_hook_cli_alias_routes_to_integration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            out = io.StringIO()
            old_stdin = os.sys.stdin
            try:
                os.sys.stdin = io.StringIO("{}")
                with redirect_stdout(out):
                    code = main(["hook", "claude-session-start", "--root", str(root)])
            finally:
                os.sys.stdin = old_stdin
            self.assertEqual(code, 0)
            self.assertEqual(code, 0)

    def test_doctor_reports_scratchpad_and_legacy_runtime_issues(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            (root / "wiki/tasks/scratchpad.md").unlink()
            (root / ".lliki").mkdir()
            report = run_doctor(root)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("missing-scratchpad", codes)
            self.assertIn("legacy-lliki-directory", codes)
            self.assertTrue(report["ok"])

    def test_doctor_accepts_compact_scratchpad_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            scratchpad = root / "wiki/tasks/scratchpad.md"
            self.assertIn("## Current State", scratchpad.read_text(encoding="utf-8"))
            report = run_doctor(root)
            self.assertNotIn("scratchpad-missing-section", {issue["code"] for issue in report["issues"]})

    def test_context_routes_from_active_scratchpad(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            task = root / "wiki/tasks/HWRD-115-sensor.md"
            task.write_text("---\nid: HWRD-115\ntitle: Sensor\nstatus: active\n---\n# Task\n", encoding="utf-8")
            scratchpad = root / "wiki/tasks/scratchpad.md"
            scratchpad.write_text(
                "# Active Task Scratchpad\n\n"
                "## Task\n\n"
                "- **ID:** HWRD-115\n"
                "- **File:** `wiki/tasks/HWRD-115-sensor.md`\n\n"
                "## Current Checkpoint\n\nValidate wake.\n\n"
                "## Confirmed Outcomes\n\n- None.\n\n"
                "## Active Blockers\n\n- None.\n\n"
                "## Focus\n\n- `src/lliki/cli.py`\n\n"
                "## Remaining Validation\n\n- Hook smoke.\n\n"
                "## Next Action\n\nRun wake test.\n\n"
                "## Snapshot\n\n- **Recorded commit:** Unknown\n- **Updated:** Unknown\n",
                encoding="utf-8",
            )
            route = context_routes(root)
            self.assertEqual(route["mode"], "resume")
            self.assertEqual(route["active_task"], "wiki/tasks/HWRD-115-sensor.md")

    def test_session_start_hook_only_returns_small_resume_context(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            task = root / "wiki/tasks/HWRD-115-sensor.md"
            task.write_text("---\nid: HWRD-115\ntitle: Sensor\nstatus: active\n---\n# Task\n", encoding="utf-8")
            (root / "wiki/tasks/scratchpad.md").write_text(
                "# Active Task Scratchpad\n\n"
                "## Task\n\n"
                "- **ID:** HWRD-115\n"
                "- **File:** `wiki/tasks/HWRD-115-sensor.md`\n\n"
                "## Current Checkpoint\n\nWake test.\n\n"
                "## Confirmed Outcomes\n\n- None.\n\n"
                "## Active Blockers\n\n- None.\n\n"
                "## Focus\n\n- None.\n\n"
                "## Remaining Validation\n\n- None.\n\n"
                "## Next Action\n\nRun wake test.\n\n"
                "## Snapshot\n\n- **Recorded commit:** Unknown\n- **Updated:** Unknown\n",
                encoding="utf-8",
            )
            old_stdin = os.sys.stdin
            try:
                os.sys.stdin = io.StringIO("{}")
                output = io.StringIO()
                with redirect_stdout(output):
                    run_hook("claude-session-start", root)
            finally:
                os.sys.stdin = old_stdin
            payload = json.loads(output.getvalue())
            context = payload["hookSpecificOutput"]["additionalContext"]
            self.assertIn("HWRD-115", context)
            self.assertLess(len(context), 2000)

    def test_bare_lliki_shows_command_overview_without_writing(self):
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp:
            before = sorted(os.listdir(temp))
            out = io.StringIO()
            try:
                os.chdir(temp)
                with redirect_stdout(out):
                    code = main([])
            finally:
                os.chdir(cwd)
            text = out.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("Commands", text)
            for name in ("init", "update", "doctor", "index", "tasks", "context", "prompt"):
                self.assertIn(name, text)
            self.assertIn("lliki --help", text)
            self.assertEqual(sorted(os.listdir(temp)), before)

    def test_help_lists_all_public_commands(self):
        out = io.StringIO()
        with redirect_stdout(out):
            with self.assertRaises(SystemExit):
                main(["--help"])
        text = out.getvalue()
        for name in ("init", "update", "doctor", "prompt", "templates", "tasks",
                     "notes", "explore", "index", "integration", "version", "context", "append"):
            self.assertIn(name, text)
        self.assertNotIn("hook", text)

    def test_bare_tasks_and_index_refresh(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            (root / "wiki/tasks/HWRD-001-x.md").write_text(
                "---\nid: HWRD-001\ntitle: X\nstatus: planned\n---\n# T\n", encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(["tasks", "--root", str(root), "--json"]), 0)
            self.assertIn("wiki/tasks/tasks-index.md", json.dumps(json.loads(out.getvalue())))
            self.assertIn("HWRD-001", (root / "wiki/tasks/tasks-index.md").read_text(encoding="utf-8"))
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(["index", "--root", str(root), "--json"]), 0)
            payload = json.loads(out.getvalue())
            for key in ("created", "refreshed", "unchanged"):
                self.assertIn(key, payload)

    def test_commands_panel_lines_are_uniform_width(self):
        from lliki.branding import render_commands_panel
        commands = [("init", "short"), ("integration", "d" * 90)]
        for width in (40, 80, 120):
            lines = render_commands_panel(commands, width=width).splitlines()
            self.assertEqual(len({len(line) for line in lines}), 1, width)

    def test_cli_default_noninteractive(self):
        with tempfile.TemporaryDirectory() as temp:
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["init", "--root", temp, "--default", "--yes"])
            self.assertEqual(code, 0)
            self.assertIn("Estimated LLM usage", output.getvalue())
            self.assertNotIn("Author: brunofbloq", output.getvalue())
            self.assertTrue((Path(temp) / "wiki/tasks/scratchpad.md").exists())
            self.assertFalse((Path(temp) / ".lliki").exists())

    def test_update_fresh_repo_creates_wiki_and_passes_doctor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report = run_update(root)
            self.assertTrue((root / "wiki/tasks/scratchpad.md").exists())
            self.assertIn("/wiki/tasks/scratchpad.md", (root / ".gitignore").read_text(encoding="utf-8"))
            self.assertFalse((root / "wiki/tasks/resume.md").exists())
            self.assertFalse((root / ".lliki").exists())
            self.assertTrue(report["doctor"]["ok"])
            self.assertFalse(report["semantic_migration_needed"])

    def test_update_is_idempotent_for_current_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run_update(root)
            second = run_update(root)
            self.assertEqual(second["actions"]["created"], [])
            self.assertEqual(second["actions"]["updated"], [])
            self.assertTrue(second["doctor"]["ok"])

    def test_update_preserves_existing_scratchpad_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            scratchpad = root / "wiki/tasks/scratchpad.md"
            original = scratchpad.read_bytes()
            report = run_update(root)
            self.assertEqual(scratchpad.read_bytes(), original)
            self.assertIn("wiki/tasks/scratchpad.md", report["actions"]["preserved"])

    def test_update_preserves_legacy_scratchpad_and_warns(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "wiki").mkdir(parents=True)
            legacy = root / "wiki/scratchpad.md"
            legacy.write_text("legacy local notes\n", encoding="utf-8")
            report = run_update(root)
            self.assertEqual(legacy.read_text(encoding="utf-8"), "legacy local notes\n")
            self.assertTrue((root / "wiki/tasks/scratchpad.md").exists())
            self.assertTrue(any("Legacy wiki/scratchpad.md" in warning for warning in report["warnings"]))

    def test_update_replaces_old_scratchpad_ignore_rule(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".gitignore").write_text(
                "# Lliki local LLM handover state\n/wiki/scratchpad.md\n",
                encoding="utf-8",
            )
            report = run_update(root)
            text = (root / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("/wiki/tasks/scratchpad.md", text)
            self.assertNotIn("/wiki/scratchpad.md", text)
            self.assertIn(".gitignore", report["actions"]["updated"])

    def test_update_legacy_repo_reports_prompt_without_rewriting_index_or_lliki(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "wiki").mkdir(parents=True)
            legacy_index = "# Project Wiki\n\n## Project Snapshot\n\n- Old.\n\n## Active Route\n\n- **Active task:** None\n"
            (root / "wiki/index.md").write_text(legacy_index, encoding="utf-8")
            (root / ".lliki").mkdir()
            report = run_update(root)
            # safe migration: manual content preserved under the new named index
            # path; only the deterministic generated region was appended.
            self.assertFalse((root / "wiki/index.md").exists())
            migrated = (root / "wiki/wiki-index.md").read_text(encoding="utf-8")
            self.assertTrue(migrated.startswith(legacy_index))
            self.assertIn("Project Snapshot", migrated)
            self.assertTrue((root / ".lliki").exists())
            self.assertTrue(report["semantic_migration_needed"])
            self.assertIn("Project Snapshot", report["legacy_index_sections"][0])
            self.assertIn("Review legacy context migration", report["migration_prompt"])

    def test_update_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
            report = run_update(root, dry_run=True)
            after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
            self.assertEqual(before, after)
            self.assertIn("wiki/tasks/scratchpad.md", report["actions"]["created"])
            self.assertEqual(report["actions"]["backups"], [])

    def test_update_cli_json_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["update", "--root", temp, "--json"])
            self.assertEqual(code, 0)
            payload = json.loads(output.getvalue())
            for key in ("root", "dry_run", "actions", "indexes", "doctor", "warnings", "semantic_migration_needed", "migration_prompt"):
                self.assertIn(key, payload)
            self.assertIn("created", payload["actions"])
            self.assertIn("migrated", payload["actions"])

    # --- 0.4 folder indexes, notes, factory, doctor, update check ---

    def test_index_refresh_creates_recursive_named_indexes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            (root / "wiki/research/vision").mkdir(parents=True)
            (root / "wiki/research/vision/experiment-a.md").write_text(
                "---\ntitle: Experiment A\n---\n# Experiment A\n", encoding="utf-8")
            from lliki.core.indexing import refresh_indexes
            result = refresh_indexes(root)
            self.assertTrue((root / "wiki/research/research-index.md").exists())
            self.assertTrue((root / "wiki/research/vision/vision-index.md").exists())
            research = (root / "wiki/research/research-index.md").read_text()
            self.assertIn("[[research/vision/vision-index]]", research)
            vision = (root / "wiki/research/vision/vision-index.md").read_text()
            self.assertIn("[[research/vision/experiment-a|Experiment A]]", vision)
            # idempotent second pass
            second = refresh_indexes(root)
            self.assertEqual(second["created"], [])
            self.assertEqual(second["refreshed"], [])

    def test_index_refresh_preserves_manual_content(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            notes_index = root / "wiki/notes/notes-index.md"
            notes_index.write_text(
                notes_index.read_text(encoding="utf-8") + "\n## Manual section\n\nKeep me.\n",
                encoding="utf-8",
            )
            from lliki.core.indexing import refresh_folder
            refresh_folder(root, root / "wiki/notes")
            text = notes_index.read_text(encoding="utf-8")
            self.assertIn("Keep me.", text)
            self.assertEqual(text.count("## Manual section"), 1)

    def test_document_factory_creates_and_indexes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            from lliki.core.documents import create_document
            note = create_document(root, "note", "Toradex modem experiment", tags=["modem"])
            self.assertRegex(note["path"], r"wiki/notes/\d{4}-\d{2}-\d{2}-toradex-modem-experiment\.md")
            content = (root / note["path"]).read_text(encoding="utf-8")
            self.assertIn("type: note", content)
            self.assertIn('tags: ["modem"]', content)
            index_text = (root / "wiki/notes/notes-index.md").read_text(encoding="utf-8")
            self.assertIn("toradex-modem-experiment", index_text)
            task = create_document(root, "task", "Implement API")
            self.assertEqual(task["id"], "LLIKI-001")
            self.assertTrue((root / task["path"]).exists())
            second = create_document(root, "task", "Second task")
            self.assertEqual(second["id"], "LLIKI-002")
            explore = create_document(root, "exploratory", "Auth alternatives")
            self.assertTrue((root / explore["path"]).exists())
            with self.assertRaises(FileExistsError):
                create_document(root, "note", "Toradex modem experiment")

    def test_notes_cli_commands(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(["notes", "new", "Modem test", "--root", str(root)]), 0)
            with redirect_stdout(out):
                self.assertEqual(main(["notes", "list", "--root", str(root)]), 0)
            self.assertIn("Modem test", out.getvalue())
            from lliki.core.notes import append_to_note, search_notes, show_note
            append_to_note(root, "modem-test", "UART works.", heading="Findings")
            self.assertIn("UART works.", show_note(root, "modem-test"))
            results = search_notes(root, "uart")
            self.assertEqual(len(results), 1)

    def test_doctor_detects_index_contract_violations(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            # WIKI001: new folder without index
            (root / "wiki/research").mkdir()
            codes = {issue["code"] for issue in run_doctor(root)["issues"]}
            self.assertIn("WIKI001-missing-folder-index", codes)
            (root / "wiki/research").rmdir()
            # WIKI003: orphan note
            (root / "wiki/notes/orphan.md").write_text("# Orphan\n", encoding="utf-8")
            codes = {issue["code"] for issue in run_doctor(root)["issues"]}
            self.assertIn("WIKI003-orphan-document", codes)
            (root / "wiki/notes/orphan.md").unlink()
            # WIKI005: stale generated region
            notes_index = root / "wiki/notes/notes-index.md"
            notes_index.write_text(
                notes_index.read_text(encoding="utf-8").replace(
                    "<!-- lliki:generated:start id=folder-index -->\n\n<!-- lliki:generated:end id=folder-index -->",
                    "<!-- lliki:generated:start id=folder-index -->\n- stale\n<!-- lliki:generated:end id=folder-index -->"),
                encoding="utf-8",
            )
            codes = {issue["code"] for issue in run_doctor(root)["issues"]}
            self.assertIn("WIKI005-stale-generated-index", codes)

    def test_doctor_flags_legacy_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            (root / "wiki/tasks/dashboard.md").write_text("# old\n", encoding="utf-8")
            codes = {issue["code"] for issue in run_doctor(root)["issues"]}
            self.assertIn("WIKI004-legacy-path", codes)

    def test_context_json_exposes_collections(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            out = io.StringIO()
            with redirect_stdout(out):
                main(["context", "--root", str(root), "--json"])
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["entry"], "wiki/wiki-index.md")
            self.assertEqual(payload["scratchpad"], "wiki/tasks/scratchpad.md")
            self.assertNotIn("resume", payload)
            self.assertEqual(payload["notes"], "wiki/notes/notes-index.md")
            for key in ("docs", "tasks", "exploratory", "notes"):
                self.assertIn(key, payload["collections"])

    def test_updatecheck_policy_no_network_first_launches(self):
        from lliki.core import updatecheck
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / "update.json"
            calls = []
            def fake_fetch(timeout: float = 2.0):
                calls.append(1)
                return "99.0.0"
            original_cache, original_fetch = updatecheck.cache_path, updatecheck.fetch_latest
            updatecheck.cache_path = lambda: cache
            updatecheck.fetch_latest = fake_fetch
            try:
                self.assertIsNone(updatecheck.update_notice("0.4.0"))  # launch 1
                self.assertIsNone(updatecheck.update_notice("0.4.0"))  # launch 2
                self.assertEqual(calls, [])
                notice = updatecheck.update_notice("0.4.0")  # launch 3 checks
                self.assertEqual(len(calls), 1)
                self.assertIn("99.0.0", notice)
                cached = updatecheck.update_notice("0.4.0")  # 24h window: serve cached notice
                self.assertIn("99.0.0", cached)
                self.assertEqual(len(calls), 1)
            finally:
                updatecheck.cache_path, updatecheck.fetch_latest = original_cache, original_fetch
        # disabled via env
        old = os.environ.get("LLIKI_NO_UPDATE_CHECK")
        os.environ["LLIKI_NO_UPDATE_CHECK"] = "1"
        try:
            self.assertIsNone(updatecheck.update_notice("0.4.0"))
        finally:
            if old is None:
                os.environ.pop("LLIKI_NO_UPDATE_CHECK", None)
            else:
                os.environ["LLIKI_NO_UPDATE_CHECK"] = old

    def test_hermes_init_prints_navigation_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = io.StringIO()
            with redirect_stdout(out):
                main(["init", "--root", str(root), "--custom", "--integrate", "hermes", "--yes"])
            text = out.getvalue()
            self.assertIn("Hermes navigation contract", text)
            self.assertIn("wiki/tasks/scratchpad.md", text)
            self.assertIn("wiki/wiki-index.md", text)

    def test_integration_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(setup_mode="custom", integrations=("generic", "hermes")), interactive=False, yes=True)
            out = io.StringIO()
            with redirect_stdout(out):
                main(["integration", "status", "--root", str(root), "--json"])
            status = json.loads(out.getvalue())
            self.assertIn("installed", status["generic"])
            self.assertIn("installed", status["hermes"])
            self.assertEqual(status["claude"], "not installed")


if __name__ == "__main__":
    unittest.main()
