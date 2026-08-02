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
from lliki.core.tasks import refresh_dashboard
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
            self.assertTrue((root / "wiki/index.md").exists())
            self.assertTrue((root / "wiki/tasks/scratchpad.md").exists())
            self.assertIn("/wiki/tasks/scratchpad.md", (root / ".gitignore").read_text(encoding="utf-8"))
            self.assertIn("/wiki/tasks/.backup/", (root / ".gitignore").read_text(encoding="utf-8"))
            self.assertFalse((root / ".lliki").exists())
            self.assertIn("embedded-systems-architect", data["prompts"][0])
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

    def test_task_dashboard_generation_and_index_pointer(self):
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
            result = refresh_dashboard(root, update_index=True)
            self.assertTrue(result["dashboard_changed"])
            self.assertEqual(result["task_count"], 1)
            self.assertFalse(result["index_changed"])
            self.assertIn("deprecated", result["warnings"][0])
            dashboard = (root / "wiki/tasks/dashboard.md").read_text()
            self.assertIn("HWRD-115", dashboard)
            self.assertNotIn("Recently Completed", dashboard)
            self.assertNotIn("HWRD-115", (root / "wiki/index.md").read_text())

    def test_dashboard_backups_are_kept_in_backup_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            task = root / "wiki/tasks/HWRD-115-sensor.md"
            task.write_text(
                "---\nid: HWRD-115\ntitle: Sensor bring-up\nstatus: active\npriority: high\n---\n# Task\n",
                encoding="utf-8",
            )
            result = refresh_dashboard(root)
            backup = Path(result["backup"])
            self.assertEqual(backup.parent, root / "wiki/tasks/.backup")
            self.assertTrue(backup.exists())
            self.assertEqual(list((root / "wiki/tasks").glob("dashboard.md.bak.*")), [])

    def test_dashboard_refresh_moves_existing_backups(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            old_backup = root / "wiki/tasks/dashboard.md.bak.old"
            old_backup.write_text("old backup\n", encoding="utf-8")
            result = refresh_dashboard(root)
            moved = root / "wiki/tasks/.backup/dashboard.md.bak.old"
            self.assertFalse(old_backup.exists())
            self.assertEqual(moved.read_text(encoding="utf-8"), "old backup\n")
            self.assertIn(moved.as_posix(), result["moved_backups"])

    def test_dashboard_refresh_dry_run_does_not_move_backups(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            old_backup = root / "wiki/tasks/dashboard.md.bak.old"
            old_backup.write_text("old backup\n", encoding="utf-8")
            result = refresh_dashboard(root, dry_run=True)
            self.assertTrue(old_backup.exists())
            self.assertFalse((root / "wiki/tasks/.backup").exists())
            expected = (root / "wiki/tasks/.backup/dashboard.md.bak.old").as_posix()
            self.assertIn(expected, result["moved_backups"])

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

    def test_state_cli_is_deprecated_stub(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["state", "show", "--root", str(root), "--json"])
            self.assertEqual(code, 2)
            payload = json.loads(output.getvalue())
            self.assertTrue(payload["deprecated"])
            self.assertEqual(payload["scratchpad"], "wiki/tasks/scratchpad.md")
            self.assertFalse((root / ".lliki").exists())

    def test_deprecated_init_options_do_not_create_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main(["init", "--root", temp, "--default", "--yes", "--scratchpad"])
            self.assertEqual(code, 0)
            self.assertIn("--scratchpad is deprecated", stderr.getvalue())
            self.assertTrue((Path(temp) / "wiki/tasks/scratchpad.md").exists())
            self.assertFalse((Path(temp) / ".lliki").exists())

        with tempfile.TemporaryDirectory() as temp:
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main(["init", "--root", temp, "--custom", "--yes", "--runtime", "assisted"])
            self.assertEqual(code, 2)
            self.assertIn("--runtime assisted/debug is deprecated", stderr.getvalue())
            self.assertFalse((Path(temp) / ".lliki").exists())

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
            self.assertFalse(second["dashboard"]["dashboard_changed"])
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
            self.assertEqual((root / "wiki/index.md").read_text(encoding="utf-8"), legacy_index)
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
            for key in ("root", "dry_run", "actions", "dashboard", "doctor", "warnings", "semantic_migration_needed", "migration_prompt"):
                self.assertIn(key, payload)
            self.assertIn("created", payload["actions"])


if __name__ == "__main__":
    unittest.main()
