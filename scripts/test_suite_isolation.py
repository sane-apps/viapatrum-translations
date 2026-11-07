#!/usr/bin/env python3
"""The tests must not take their answers from this machine's live state.

Two checks: no test module changes a shared module at import time, and the money-safety tests give the same
result whatever the owner's Cloudflare switch files say. The second runs them with HOME pointed at a temp folder,
with no Cloudflare tokens and with the network refused. Run: python3 scripts/test_suite_isolation.py
"""
import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

# spend_guard_allow_test.py does not match discover's test_*.py, so this is also what runs it in the suite.
GUARD_TESTS = ["test_spend_guard", "spend_guard_allow_test", "test_cf_batch_broker", "test_dual_family_review"]

RUN_OFFLINE = """
import socket, sys, unittest
def refuse(*a, **k):
    raise AssertionError("a money-safety test tried to use the network")
socket.socket.connect = socket.socket.connect_ex = socket.getaddrinfo = refuse
unittest.main(module=None, argv=["unittest", "-q"] + sys.argv[1:])
"""


def run_guard_tests(home: Path) -> subprocess.CompletedProcess:
    drop = ("CLOUDFLARE_API_TOKEN", "CF_TOKEN", "CLOUDFLARE_ACCOUNT_ID", "TYPESAFE_API_KEY",
            "SANE_CF_AI_OFF_FILE", "SANE_CF_AI_ALLOW_FILE", "FATHERS_DAILY_CAP_USD")
    env = {k: v for k, v in os.environ.items() if k not in drop}
    env["HOME"] = str(home)
    return subprocess.run([sys.executable, "-c", RUN_OFFLINE, *GUARD_TESTS], cwd=SCRIPTS, env=env,
                          capture_output=True, text=True, timeout=120)


def snapshot(home: Path) -> dict:
    return {str(p): p.read_bytes() for p in home.rglob("*") if p.is_file()}


class NoStubsAtImport(unittest.TestCase):
    def test_no_test_module_sets_a_module_attribute_at_import(self):
        """discover imports every test module before running any test, so `spend_guard.allow = stub` at the top
        of one file turned the spend gate off for all of them. Use setUpModule and _testenv.stub_for_module."""
        found = []
        for path in sorted(SCRIPTS.glob("test_*.py")):
            for node in ast.parse(path.read_text(encoding="utf-8")).body:
                targets = node.targets if isinstance(node, ast.Assign) else []
                found += [f"{path.name}:{node.lineno}" for t in targets if isinstance(t, ast.Attribute)]
        self.assertEqual(found, [])


class GuardTestsIgnoreTheRealSwitch(unittest.TestCase):
    def check(self, files: dict):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            for rel, text in files.items():
                (home / rel).parent.mkdir(parents=True, exist_ok=True)
                (home / rel).write_text(text)
            before = snapshot(home)
            p = run_guard_tests(home)
            self.assertEqual(p.returncode, 0, p.stderr[-3000:])
            self.assertEqual(snapshot(home), before, "a test wrote under HOME")

    def test_empty_home(self):
        self.check({})

    def test_switched_off(self):
        self.check({".sane/CLOUDFLARE_AI_OFF": "off"})

    def test_switched_off_with_everyone_allowed(self):
        self.check({".sane/CLOUDFLARE_AI_OFF": "off", ".sane/CLOUDFLARE_AI_ALLOW": "*\towner's words\t2026-11-04\n"})


if __name__ == "__main__":
    unittest.main()
