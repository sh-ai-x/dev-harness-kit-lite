"""state_codec.py — phase/step status transitions for dev-kit-lite.

Pruned from full kit's lib/state_codec.py. Lite has 6 stages:
  bootstrap → plan → ci-setup → build-tdd → review → build-verify

Plus cross-stage skills: plan-update, reassign (do not have their own status).
"""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class Stage(str, Enum):
    BOOTSTRAP = "bootstrap"
    PLAN = "plan"
    CI_SETUP = "ci-setup"
    BUILD_TDD = "build-tdd"
    REVIEW = "review"
    BUILD_VERIFY = "build-verify"


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"
    BLOCKED = "blocked"


# Valid status transitions (machine-enforced)
VALID_TRANSITIONS: dict[StepStatus, set[StepStatus]] = {
    StepStatus.PENDING: {StepStatus.IN_PROGRESS, StepStatus.BLOCKED},
    StepStatus.IN_PROGRESS: {StepStatus.COMPLETED, StepStatus.ERROR, StepStatus.BLOCKED},
    StepStatus.COMPLETED: set(),  # terminal
    StepStatus.ERROR: {StepStatus.PENDING, StepStatus.IN_PROGRESS},  # retry allowed
    StepStatus.BLOCKED: {StepStatus.PENDING, StepStatus.IN_PROGRESS},  # unblock allowed
}


@dataclass
class StepState:
    n: int
    title: str
    role: str  # FE | BE | Design | PM
    owner: str
    branch: str
    worktree: str
    acs: list[str]
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    blocked_reason: Optional[str] = None

    def can_transition_to(self, next_status: StepStatus) -> bool:
        return next_status in VALID_TRANSITIONS[self.status]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "StepState":
        d = dict(d)
        d["status"] = StepStatus(d.get("status", "pending"))
        return cls(**d)


def write_index(phase: str, steps: list[StepState], root: Path = Path(".dev-kit")) -> Path:
    """Write phases/<phase>/index.json."""
    out = root / "phases" / phase / "index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "phase": phase,
        "generated_at": _now_iso(),
        "steps": [s.to_dict() for s in steps],
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return out


def read_index(phase: str, root: Path = Path(".dev-kit")) -> list[StepState]:
    p = root / "phases" / phase / "index.json"
    payload = json.loads(p.read_text())
    return [StepState.from_dict(s) for s in payload.get("steps", [])]


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
