"""execute.py — minimal stage runner for dev-kit-lite.

Pruned from full kit's lib/execute.py. Lite runs 6 stages sequentially;
no auto-classifier, no per-step worktree management (hooks handle that).

Usage:
    python3 -m lib.execute <stage>
where stage in: bootstrap, plan, ci-setup, build-tdd, review, build-verify
"""
from __future__ import annotations
import sys
import subprocess
from pathlib import Path

STAGES = ["bootstrap", "plan", "ci-setup", "build-tdd", "review", "build-verify"]


def run_stage(stage: str) -> int:
    if stage not in STAGES:
        print(f"unknown stage: {stage}; valid: {STAGES}")
        return 2
    print(f"[dev-kit-lite] running stage: {stage}")
    # Each stage is a slash-command invocation in Claude Code / Codex.
    # This module is the lib-runtime that stages call into for state mgmt.
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: python3 -m lib.execute <stage>  (valid: {STAGES})")
        sys.exit(2)
    sys.exit(run_stage(sys.argv[1]))
