#!/usr/bin/env python3
"""Tests for muse_native.py. No model call."""
import json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import muse_native as mn


def tool(cmd, rc=0):
    return json.dumps({"payload": {"kind": "tool_result", "text": json.dumps({"command": cmd, "exit_code": rc})}})


class Audit(unittest.TestCase):
    def test_lists_commands_and_flags_only_paths_outside_the_allowed_folders(self):
        with tempfile.TemporaryDirectory() as td:
            ws = os.path.join(td, "ws"); os.mkdir(ws)
            venv = os.path.join(td, "venv"); os.mkdir(venv)
            ev = os.path.join(ws, "ev.jsonl")
            home = os.path.expanduser("~")
            with open(ev, "w") as f:
                f.write("\n".join([tool("pwd"), tool(f"cat {ws}/a.txt"), tool(f"{venv}/bin/python x.py"),
                                   tool(f"ls {home}/.ssh | head -3"), tool("cat ~/.zsh_history", 1), "not json",
                                   json.dumps({"payload": {"kind": "run_terminal", "terminal": "completed", "text": "done"}})]))
            cmds, outside = mn.audit(ev, ws, allowed_roots=[venv])
            self.assertEqual(len(cmds), 5)
            self.assertEqual(sorted(o["path"] for o in outside), sorted([f"{home}/.ssh", "~/.zsh_history"]))

    def test_refuses_an_unknown_model_and_the_home_folder_as_workspace(self):
        with self.assertRaises(ValueError):
            mn.run_native("muse-not-a-model", "x", os.path.expanduser("~/.cache"))
        with self.assertRaises(ValueError):
            mn.run_native("muse-wonder-full-1.0", "plain task", os.path.expanduser("~"))


if __name__ == "__main__":
    unittest.main()
