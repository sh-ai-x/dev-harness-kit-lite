"""test_phase_state.py — regression for lib/state_codec.py transitions."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.state_codec import StepState, StepStatus, VALID_TRANSITIONS


def test_pending_to_in_progress():
    s = StepState(n=1, title="x", role="FE", owner="alice", branch="feat/web-alice-x", worktree=".worktrees/web-alice", acs=["AC-1"])
    assert s.status == StepStatus.PENDING
    assert s.can_transition_to(StepStatus.IN_PROGRESS)


def test_in_progress_to_completed():
    s = StepState(n=1, title="x", role="FE", owner="alice", branch="feat/web-alice-x", worktree=".worktrees/web-alice", acs=["AC-1"], status=StepStatus.IN_PROGRESS)
    assert s.can_transition_to(StepStatus.COMPLETED)


def test_completed_is_terminal():
    s = StepState(n=1, title="x", role="FE", owner="alice", branch="feat/web-alice-x", worktree=".worktrees/web-alice", acs=["AC-1"], status=StepStatus.COMPLETED)
    for next_status in StepStatus:
        assert not s.can_transition_to(next_status), f"completed should not transition to {next_status}"


def test_error_can_retry():
    s = StepState(n=1, title="x", role="FE", owner="alice", branch="feat/web-alice-x", worktree=".worktrees/web-alice", acs=["AC-1"], status=StepStatus.ERROR)
    assert s.can_transition_to(StepStatus.PENDING)
    assert s.can_transition_to(StepStatus.IN_PROGRESS)


def test_blocked_can_unblock():
    s = StepState(n=1, title="x", role="FE", owner="alice", branch="feat/web-alice-x", worktree=".worktrees/web-alice", acs=["AC-1"], status=StepStatus.BLOCKED)
    assert s.can_transition_to(StepStatus.PENDING)


def test_to_from_dict_roundtrip():
    s = StepState(n=2, title="y", role="BE", owner="carol", branch="feat/api-carol-y", worktree=".worktrees/api-carol", acs=["AC-2"], status=StepStatus.IN_PROGRESS, started_at="2026-09-01T18:00:00Z")
    d = s.to_dict()
    s2 = StepState.from_dict(d)
    assert s2.n == s.n
    assert s2.owner == s.owner
    assert s2.status == StepStatus.IN_PROGRESS
