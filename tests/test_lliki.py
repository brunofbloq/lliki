from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from lliki.cli import main
from lliki.branding import AUTHOR, banner_enabled, render_welcome
from lliki.core.bootstrap import initialize_repository
from lliki.core.doctor import run_doctor
from lliki.core.models import SetupConfig
from lliki.core.prompts import estimate_prompt_tokens, load_prompts
from lliki.core.resources import export_built_in_templates, validate_template_pack
from lliki.core.tasks import refresh_dashboard
from lliki.hooks import run_hook


class LlikiTests(unittest.TestCase):

    def test_welcome_banner_contains_branding_and_compact_fallback(self):
        large = render_welcome(100)
        compact = render_welcome(60)
        self.assertIn("Author: brunofbloq", large)
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
            self.assertFalse((root / ".lliki").exists())
            self.assertFalse((root / "wiki/scratchpad.md").exists())
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

    def test_custom_debug_setup_is_opt_in(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = SetupConfig(
                setup_mode="custom",
                runtime_mode="debug",
                scratchpad=True,
                integrations=("generic", "claude", "hermes"),
                claude_hooks=True,
            )
            initialize_repository(root, config, interactive=False, yes=True)
            self.assertTrue((root / ".lliki/state.json").exists())
            self.assertTrue((root / ".lliki/scratchpad.md").exists())
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertTrue((root / ".hermes.md").exists())
            settings = json.loads((root / ".claude/settings.json").read_text())
            self.assertIn("SessionStart", settings["hooks"])
            self.assertIn("/.lliki/", (root / ".gitignore").read_text())

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
            task = root / "wiki/tasks/HWRD-115-sensor.md"
            task.write_text(
                "---\nid: HWRD-115\ntitle: Sensor bring-up\nstatus: active\npriority: high\nupdated: 2026-07-31\n---\n# Task\n",
                encoding="utf-8",
            )
            result = refresh_dashboard(root, update_index=True)
            self.assertTrue(result["dashboard_changed"])
            self.assertTrue(result["index_changed"])
            self.assertIn("HWRD-115", (root / "wiki/tasks/dashboard.md").read_text())
            self.assertIn("HWRD-115", (root / "wiki/index.md").read_text())

    def test_template_export_and_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "templates"
            export_built_in_templates(destination)
            self.assertTrue((destination / "CLAUDE.md").exists())
            self.assertEqual(validate_template_pack(destination), [])

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
            broken = [i for i in report["issues"] if i["code"] == "broken-wiki-link"]
            self.assertEqual(broken, [])

    def test_legacy_inspection_does_not_report_wiki_tasks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(root, SetupConfig(), interactive=False, yes=True)
            from lliki.core.inspection import find_legacy_locations
            found = find_legacy_locations(root)
            self.assertNotIn("wiki/tasks", found["legacy_dirs"])

    def test_runtime_state_cli_helpers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            initialize_repository(
                root,
                SetupConfig(setup_mode="custom", runtime_mode="assisted"),
                interactive=False,
                yes=True,
            )
            from lliki.core.runtime import set_state_fields, read_state
            set_state_fields(root, active_task="HWRD-115", next_action="Validate wake")
            state = read_state(root)
            self.assertEqual(state["active_task"], "HWRD-115")
            self.assertEqual(state["next_action"], "Validate wake")

    def test_session_start_hook_only_returns_small_resume_context(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = SetupConfig(setup_mode="custom", runtime_mode="assisted")
            initialize_repository(root, config, interactive=False, yes=True)
            state_path = root / ".lliki/state.json"
            state = json.loads(state_path.read_text())
            state.update({"active_task": "HWRD-115", "next_action": "Run wake test"})
            state_path.write_text(json.dumps(state), encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
