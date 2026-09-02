"""test_tdd_guard.py — regression for hooks/tdd-guard.sh + lib/tdd_cycle.py."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
import pytest

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "tdd-guard.sh"


def _run_hook(payload: dict, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=5,
        cwd=str(cwd),
    )


def test_test_file_always_allowed(tmp_path):
    """Test files are allowed in any phase."""
    for phase in ["red", "green", "refactor", ""]:
        cycle = tmp_path / ".dev-kit" / ".tdd-cycle.json"
        cycle.parent.mkdir(parents=True, exist_ok=True)
        cycle.write_text(json.dumps({"phase": phase, "last_exit_code": 1}))
        for path in ["tests/test_x.py", "x_test.py", "test_x.py", "src/foo.test.ts"]:
            res = _run_hook({"tool_name": "Edit", "tool_input": {"file_path": path}}, tmp_path)
            assert res.returncode == 0, f"test path {path} should be allowed in phase={phase}"


def test_prod_code_in_red_denied(tmp_path):
    """Prod code edit in RED phase → deny."""
    cycle = tmp_path / ".dev-kit" / ".tdd-cycle.json"
    cycle.parent.mkdir(parents=True, exist_ok=True)
    cycle.write_text(json.dumps({"phase": "red", "last_exit_code": 1}))
    res = _run_hook({"tool_name": "Edit", "tool_input": {"file_path": "src/api.py"}}, tmp_path)
    if subprocess.run(["which", "jq"], capture_output=True).returncode == 0:
        assert res.returncode == 2
        assert "permissionDecision" in res.stderr


def test_prod_code_in_green_requires_prior_red(tmp_path):
    """GREEN without prior RED evidence → deny."""
    cycle = tmp_path / ".dev-kit" / ".tdd-cycle.json"
    cycle.parent.mkdir(parents=True, exist_ok=True)
    # No prior red — green but no exit_code
    cycle.write_text(json.dumps({"phase": "green", "last_exit_code": 0}))
    res = _run_hook({"tool_name": "Edit", "tool_input": {"file_path": "src/api.py"}}, tmp_path)
    if subprocess.run(["which", "jq"], capture_output=True).returncode == 0:
        assert res.returncode == 2


def test_prod_code_in_refactor_allowed(tmp_path):
    """Refactor allows edits (build-verify confirms tests still pass)."""
    cycle = tmp_path / ".dev-kit" / ".tdd-cycle.json"
    cycle.parent.mkdir(parents=True, exist_ok=True)
    cycle.write_text(json.dumps({"phase": "refactor", "last_exit_code": 0}))
    res = _run_hook({"tool_name": "Edit", "tool_input": {"file_path": "src/api.py"}}, tmp_path)
    assert res.returncode == 0


def test_no_cycle_json_denies(tmp_path):
    """No .tdd-cycle.json → fail closed (deny prod code)."""
    res = _run_hook({"tool_name": "Edit", "tool_input": {"file_path": "src/api.py"}}, tmp_path)
    if subprocess.run(["which", "jq"], capture_output=True).returncode == 0:
        assert res.returncode == 2
