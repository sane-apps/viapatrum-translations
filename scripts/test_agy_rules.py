#!/usr/bin/env python3
"""Known-answer tests (21 Nov 2026): lane model calls (agy, Claude, Muse) never carry our agent rule files.

agy loads ~/.gemini/GEMINI.md (a link to our agent rulebook) into every call as rules it must follow. The lane
sandbox denies reading those files and their link targets. No model call. Run: python3 scripts/test_agy_rules.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan_calls as pc  # noqa: E402


def _cat_in(profile: str, path: Path) -> int:
    return subprocess.run([pc.SANDBOX_EXEC, "-p", profile, "/bin/cat", str(path)],
                          capture_output=True, timeout=20).returncode


class AgyRuleFilesTest(unittest.TestCase):
    def test_profile_names_every_rule_file(self):
        for name in ("GEMINI.md", "AGENTS.md"):
            self.assertIn(f'(literal "{Path.home() / ".gemini" / name}")', pc.AGY_SANDBOX)
            self.assertIn(f'(literal "{Path.home() / ".gemini" / "config" / name}")', pc.AGY_SANDBOX)

    def test_link_target_is_denied_too(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "rulebook.md"
            target.write_text("Speak in plain English.")
            link = Path(d) / "GEMINI.md"
            link.symlink_to(target)
            with mock.patch.object(pc, "AGY_RULE_FILES", [link]):
                paths = pc._rule_paths()
            self.assertIn(str(link), paths)
            self.assertIn(str(target.resolve()), paths)
            prof = ('(version 1)(allow default)(deny file-read* '
                    + " ".join(f'(literal "{x}")' for x in paths) + ')')
            self.assertEqual(_cat_in("(version 1)(allow default)", link), 0)   # readable without the deny
            self.assertNotEqual(_cat_in(prof, link), 0)                         # through the link: denied
            self.assertNotEqual(_cat_in(prof, target.resolve()), 0)             # the target itself: denied

    def test_live_rule_file_is_unreadable_in_the_lane_sandbox(self):
        f = Path.home() / ".gemini" / "GEMINI.md"
        if not (f.exists() or f.is_symlink()):
            self.skipTest("no ~/.gemini/GEMINI.md on this Mac")
        self.assertNotEqual(_cat_in(pc.AGY_SANDBOX, f), 0)

    def test_other_files_stay_readable(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as t:
            t.write("ok")
        self.assertEqual(_cat_in(pc.AGY_SANDBOX, Path(t.name)), 0)


class ClaudeInstructionFilesTest(unittest.TestCase):
    def test_claude_calls_run_in_safe_mode(self):
        seen = {}

        def fake_run(cmd, **kw):
            seen["cmd"] = cmd
            return subprocess.CompletedProcess(cmd, 0, stdout='{"result": "ok", "is_error": false}', stderr="")
        with mock.patch.object(pc.subprocess, "run", fake_run):
            text, err = pc._run_claude("claude-sonnet-5-5", "sys", "hello")
        self.assertEqual((text, err), ("ok", False))
        self.assertIn("--safe-mode", seen["cmd"])
        self.assertNotIn("--bare", seen["cmd"])   # --bare cannot use the plan sign-in


class MuseInstructionFilesTest(unittest.TestCase):
    def test_muse_drafts_leave_out_other_programs_rule_files(self):
        import muse_runner as mr
        seen = {}

        def fake_run(cmd, **kw):
            seen["cmd"] = cmd
            return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")
        with tempfile.TemporaryDirectory() as d:
            q = Path(d)
            mr.dirs(q)
            job = q / "in" / "j1.json"
            job.write_text(json.dumps({"prompt": "hello", "effort": "medium"}))
            with mock.patch.object(mr.subprocess, "run", fake_run):
                res = mr.run_job(q, job)
        self.assertEqual(res["answer"], "ok")
        self.assertIn("--no-foreign-personal-context", seen["cmd"])
        self.assertIn("--preset", seen["cmd"])


class GrokLaneSetupTest(unittest.TestCase):
    """grok inspect (no model call) in the lane folder with the lane settings: nothing but the prompt goes in."""

    def inspect(self):
        import os
        pc._grok_lane_folder()
        env = dict(os.environ, **pc.GROK_LANE_ENV)
        r = subprocess.run([pc.GROK, "inspect"], capture_output=True, text=True, cwd=str(pc.GROK_CWD), env=env,
                           timeout=90)
        return r.stdout

    def section(self, out, title):
        lines, keep = [], False
        for ln in out.splitlines():
            if ln.strip().startswith(title):
                keep = True
                continue
            if keep and ln.strip() and not ln.strip().startswith("\u2514"):
                break
            if keep and ln.strip():
                lines.append(ln)
        return lines

    def test_lane_env_turns_off_memory_compat_and_inbox_hook(self):
        self.assertEqual(pc.GROK_LANE_ENV["GROK_MEMORY"], "0")
        self.assertEqual(pc.GROK_LANE_ENV["AGENT_COMMS_OFF"], "1")
        for k in ("AGENTS", "RULES", "SKILLS", "MCPS", "HOOKS"):
            self.assertEqual(pc.GROK_LANE_ENV[f"GROK_CLAUDE_{k}_ENABLED"], "0")

    def test_lane_config_names_every_user_server(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "config.toml"
            cfg.write_text('[mcp_servers.alpha]\ncommand = "x"\n[mcp_servers.beta]\nurl = "https://e"\n')
            text = pc.grok_lane_config(cfg)
        import tomllib
        got = tomllib.loads(text)["mcp_servers"]
        self.assertFalse(got["alpha"]["enabled"])
        self.assertFalse(got["beta"]["enabled"])

    def test_live_inspect_shows_no_rules_servers_or_plugins(self):
        if not Path(pc.GROK).exists():
            self.skipTest("no grok on this Mac")
        out = self.inspect()
        for ln in self.section(out, "Project Instructions"):
            self.assertIn("[disabled]", ln, ln)
        for ln in self.section(out, "MCP Servers"):
            self.assertIn("[disabled]", ln, ln)
        for ln in self.section(out, "Plugins"):
            self.assertTrue("disabled" in ln, ln)


if __name__ == "__main__":
    unittest.main(verbosity=1)
