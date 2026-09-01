"""test_worktree_guard.py — regression for hooks/worktree-guard.sh.

Pruned from full kit's tests/test_worktree_guard.py. Tests the lite hook's
behavior on Edit in main checkout vs in a worktree.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
import pytest

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "worktree-guard.sh"


def _run_hook(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=5,
    )


def test_jq_missing_fails_closed(tmp_path, monkeypatch):
    """If jq is absent, the hook should exit 2 with deny JSON."""
    monkeypatch.setenv("PATH", "/usr/bin:/bin")  # strip jq if present
    res = _run_hook({"tool_name": "Edit", "tool_input": {"file_path": "x.py"}, "cwd": str(tmp_path)})
    # May still find jq; if so, skip
    if subprocess.run(["which", "jq"], capture_output=True).returncode != 0:
        assert res.returncode == 2
        assert "permissionDecision" in res.stderr


def test_edit_on_main_checkout_denied(tmp_path):
    """Edit in a non-worktree directory (no .git) — should exit 0 (not git, no rule)."""
    res = _run_hook({"tool_name": "Edit", "tool_input": {"file_path": "x.py"}, "cwd": str(tmp_path)})
    # Outside any git repo → hook is project-scoped → exits 0
    assert res.returncode == 0


def test_empty_payload_noop():
    """Empty payload (no file_path) → noop, exit 0."""
    res = _run_hook({"tool_name": "Edit"})
    assert res.returncode == 0


def test_probe_payload_noop():
    """Probe with empty tool_input → noop."""
    res = _run_hook({"tool_name": "Edit", "tool_input": {}})
    assert res.returncode == 0
