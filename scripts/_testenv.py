"""Set-up shared by the offline tests. Not a test file.

Importing this makes llm_vendor_gate findable under any HOME. work_pipeline and work_read look for it only
under ~/SaneApps/infra/SaneProcess/scripts, so with another HOME they fail on import. Tests find the same
file by the repo's position instead. The HOME path stays first, so a normal run loads what it always loaded.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

SANEPROCESS_SCRIPTS = Path(__file__).resolve().parents[3] / "infra/SaneProcess/scripts"

if str(SANEPROCESS_SCRIPTS) not in sys.path:
    sys.path.append(str(SANEPROCESS_SCRIPTS))


def stub_for_module(target, **attrs) -> None:
    """Call from setUpModule. Replaces attrs until this test module ends.

    A plain `spend_guard.allow = ...` at import time lasts for the whole discover run: every test module is
    imported before the first test runs, so that stub silently turned off the gate that test_spend_guard checks.
    """
    for name, value in attrs.items():
        patcher = mock.patch.object(target, name, value)
        patcher.start()
        unittest.addModuleCleanup(patcher.stop)
