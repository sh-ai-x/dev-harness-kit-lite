"""tdd_cycle.py — RED/GREEN/REFACTOR phase tracker for dev-kit-lite.

Pruned from full kit's lib/tdd_cycle.py + lib/tdd_scope_policy.py.
Lite uses a single .dev-kit/.tdd-cycle.json (no per-step scope split).
"""
from __future__ import annotations
import json
import subprocess
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class TDDPhase(str, Enum):
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"


CYCLE_PATH = Path(".dev-kit/.tdd-cycle.json")


@dataclass
class TDDCycle:
    phase: TDDPhase
    last_exit_code: int
    test_command: str
    started_at: str
    test_count: int = 0
    passed_count: int = 0
    failed_count: int = 0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["phase"] = self.phase.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "TDDCycle":
        d = dict(d)
        d["phase"] = TDDPhase(d["phase"])
        return cls(**d)


def load() -> Optional[TDDCycle]:
    if not CYCLE_PATH.exists():
        return None
    return TDDCycle.from_dict(json.loads(CYCLE_PATH.read_text()))


def save(cycle: TDDCycle) -> None:
    CYCLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CYCLE_PATH.write_text(json.dumps(cycle.to_dict(), indent=2, sort_keys=True))


def transition(next_phase: TDDPhase, test_command: str) -> TDDCycle:
    """Transition to the next phase and run the test command to capture exit code."""
    from datetime import datetime, timezone
    proc = subprocess.run(test_command, shell=True, capture_output=True, text=True)
    cycle = TDDCycle(
        phase=next_phase,
        last_exit_code=proc.returncode,
        test_command=test_command,
        started_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    save(cycle)
    return cycle


def reset() -> None:
    """Clear the TDD cycle (used when starting a new step)."""
    if CYCLE_PATH.exists():
        CYCLE_PATH.unlink()


def red(test_command: str) -> TDDCycle:
    """Mark phase=red and run the test (must fail to satisfy L1)."""
    return transition(TDDPhase.RED, test_command)


def green(test_command: str) -> TDDCycle:
    """Mark phase=green and run the test (must pass to satisfy L1)."""
    return transition(TDDPhase.GREEN, test_command)


def refactor(test_command: str) -> TDDCycle:
    """Mark phase=refactor and run the test (must still pass)."""
    return transition(TDDPhase.REFACTOR, test_command)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python3 -m lib.tdd_cycle {red|green|refactor|reset} [-- <test_command>]")
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "reset":
        reset()
        print("TDD cycle reset")
        sys.exit(0)
    rest = sys.argv[2:]
    if "--" in rest:
        idx = rest.index("--")
        test_cmd = " ".join(rest[idx + 1:])
    else:
        test_cmd = " ".join(rest)
    if not test_cmd:
        print(f"usage: python3 -m lib.tdd_cycle {cmd} -- <test_command>")
        sys.exit(2)
    cycle = transition(TDDPhase(cmd), test_cmd)
    print(f"phase={cycle.phase.value} exit_code={cycle.last_exit_code}")
    sys.exit(0 if cycle.last_exit_code == 0 else 1)
