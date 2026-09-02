"""Pytest configuration for the synchronization test.

Uses a throwaway SQLite database so the test is fully self-contained
and does not require Supabase credentials or a running server.
"""
import os
import sys

# Force a fresh SQLite DB before any app import
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_sync.db"
os.environ["DEBUG"] = "false"

# Make the backend root importable
_BACKROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(_BACKROOT))

# Remove any stale test DB
if os.path.exists("test_sync.db"):
    os.remove("test_sync.db")


# ── Shared E2E test log ─────────────────────────────────────────
# Every test file (test_sync.py, test_notifications.py,
# test_e2e_channels.py) writes its results here via log_result(), so
# tests/test_log.csv ends up as ONE unified, dated log across all
# 4 channels and all 4 risk tiers -- the artifact shown at the demo
# as proof the whole system works end to end, not just in pieces.
import csv
from datetime import datetime, timezone

TEST_LOG_PATH = os.path.join(os.path.dirname(__file__), "test_log.csv")
_SESSION_LOG_ROWS: list[dict] = []


def log_result(channel, risk_tier, expected, actual, passed):
    """Append one row to the shared, in-memory E2E test log."""
    _SESSION_LOG_ROWS.append({
        "channel": channel,
        "risk_tier": risk_tier,
        "expected_recipients": ",".join(sorted(expected)) if expected else "",
        "actual_recipients": ",".join(sorted(actual)) if actual else "",
        "pass_fail": "PASS" if passed else "FAIL",
        "date": datetime.now(timezone.utc).isoformat(),
    })


def pytest_sessionfinish(session, exitstatus):
    """Write the accumulated log to disk once, after the whole test
    session has finished, so results from every test file are combined
    into a single dated CSV rather than each file overwriting the last."""
    if not _SESSION_LOG_ROWS:
        return
    with open(TEST_LOG_PATH, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["channel", "risk_tier", "expected_recipients",
                        "actual_recipients", "pass_fail", "date"],
        )
        writer.writeheader()
        writer.writerows(_SESSION_LOG_ROWS)
