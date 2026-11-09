#!/bin/sh
# The pytest-style tests unittest cannot collect (readiness review F8, 2026-11-07); needs pytest in .venv.
# The Muse tests (test_muse_tiebreak, test_muse_nightly, test_muse_review) are left out: Muse is retired.
cd "$(dirname "$0")/.." && exec .venv/bin/python -m pytest -q -p no:cacheprovider pipeline/test_output_guard.py pipeline/tests/test_pb_sync_db.py pipeline/tests/test_heading_links.py pipeline/tests/test_pbb_guards.py "$@"
