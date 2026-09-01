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
