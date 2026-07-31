from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from typing import Optional
from pathlib import Path


class CLISubprocessTests(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Optional[str] = None):
        env = os.environ.copy()
        source = str(Path(__file__).resolve().parents[1] / "src")
        env["PYTHONPATH"] = source + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "lliki", *args],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_inspect_json(self):
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, ".context").mkdir()
            result = self.run_cli("inspect", "--root", temp, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('".context"', result.stdout)

    def test_prompt_show(self):
        result = self.run_cli("prompt", "show", "complete-task")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Expected total call", result.stdout)

    def test_templates_diff_after_init(self):
        with tempfile.TemporaryDirectory() as temp:
            init = self.run_cli("init", "--root", temp, "--default", "--yes")
            self.assertEqual(init.returncode, 0, init.stderr)
            diff = self.run_cli("templates", "diff", "--root", temp)
            self.assertEqual(diff.returncode, 0, diff.stdout + diff.stderr)


if __name__ == "__main__":
    unittest.main()
