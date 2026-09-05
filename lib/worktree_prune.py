"""worktree_prune.py — enumerate + age-sort worktree candidates.

Companion to ``bin/worktree-prune.sh``. Owns the deterministic half:
parse ``git worktree list --porcelain`` once, build a branch→epoch
map with one ``git for-each-ref`` call, exclude the main checkout
and detached-HEAD rows, and return rows sorted oldest-first.

Pruned from dev-harness-kit's lib/worktree_prune.py (197 LOC).
Keeps the public API (``collect``, ``render_table``) and the three
CLI modes the shell script depends on; drops the committer-date
verification, JSON-error envelope, and find-ref duplicate detection
that lite's janitor workflow does not need.

CLI surface (kept stable so bin/worktree-prune.sh ports verbatim):

* (default)         — JSON list of {path, branch, epoch, sha}
* ``--table``       — fixed-width human-readable table; accepts ``--head N``
* ``--count``       — single integer (total candidates)

Returns exit 0 always (callers decide what is an error).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class Row:
    """One removable worktree, oldest-first ready."""

    path: str
    branch: str
    epoch: int
    sha: str

    def age_days(self, now_epoch: int) -> int:
        if not self.epoch or self.epoch > now_epoch:
            return 0
        return (now_epoch - self.epoch) // 86400


def _run(cmd: list[str], cwd: str) -> str:
    out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    return out.stdout


def _porcelain_blocks(stdout: str) -> Iterator[dict[str, str]]:
    """Yield one dict per porcelain block (Key value lines + blank line)."""
    block: dict[str, str] = {}
    for raw in stdout.splitlines():
        if raw == "":
            if block:
                yield block
                block = {}
            continue
        key, _, value = raw.partition(" ")
        if key == "detached":
            block["detached"] = "true"
        else:
            # Strip ``refs/heads/`` so the branch key matches the short
            # form emitted by ``git for-each-ref %(refname:short)``.
            if key == "branch" and value.startswith("refs/heads/"):
                value = value[len("refs/heads/"):]
            block[key] = value
    if block:
        yield block


def _branch_epoch_map(repo_root: str) -> dict[str, int]:
    """Single ``git for-each-ref`` call → ``{branch: epoch}``.

    Empty dict on failure (corrupt refs / no heads); callers treat
    ``epoch=0`` as "unknown" and still emit the row.
    """
    try:
        out = _run(
            [
                "git", "-C", repo_root, "for-each-ref",
                "--format=%(committerdate:unix) %(refname:short)",
                "refs/heads/",
            ],
            cwd=repo_root,
        )
    except subprocess.CalledProcessError:
        return {}
    result: dict[str, int] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        epoch_s, _, branch = line.partition(" ")
        if not branch:
            continue
        try:
            result[branch] = int(epoch_s)
        except ValueError:
            continue
    return result


def _resolve_main(repo_root: str) -> str:
    """Canonical absolute path of repo toplevel — used to exclude main."""
    return str(Path(_run(["git", "-C", repo_root, "rev-parse", "--show-toplevel"], cwd=repo_root).strip()).resolve())


def collect(repo_root: str) -> list[Row]:
    """Return removable worktree rows, oldest first.

    Excludes the main checkout and detached-HEAD worktrees (no
    branch tip to age-compare).
    """
    porcelain = _run(["git", "-C", repo_root, "worktree", "list", "--porcelain"], cwd=repo_root)
    epoch_map = _branch_epoch_map(repo_root)
    main_abs = _resolve_main(repo_root)

    rows: list[Row] = []
    for block in _porcelain_blocks(porcelain):
        path = block.get("worktree", "")
        branch = block.get("branch", "")
        sha = block.get("HEAD", "")
        if not path or not branch or block.get("detached"):
            continue
        try:
            path_abs = str(Path(path).resolve())
        except OSError:
            path_abs = path
        if path_abs == main_abs:
            continue
        rows.append(Row(path=path, branch=branch, epoch=epoch_map.get(branch, 0), sha=sha))

    rows.sort(key=lambda r: r.epoch)
    return rows


def render_table(rows: list[Row], now_epoch: int, head: int | None = None) -> str:
    """Plain-text table; oldest first. No ANSI — grep/cut-friendly."""
    if not rows:
        return ""

    def _truncate(s: str, n: int) -> str:
        return s if len(s) <= n else s[: n - 3] + "..."

    shown = rows if head is None else rows[:head]
    lines: list[str] = []
    lines.append(f"{'#':>4}  {'AGE(d)':>6}  {'BRANCH':<30}  PATH")
    lines.append(f"{'----':>4}  {'------':>6}  {'-' * 30}  {'-' * 4}")
    for i, row in enumerate(shown, start=1):
        age = row.age_days(now_epoch)
        branch = _truncate(row.branch, 30)
        lines.append(f"{i:>4}  {age:>6}  {branch:<30}  {row.path}")
    return "\n".join(lines)


def _now_epoch() -> int:
    """Wall-clock now as Unix epoch. Wrapped so tests can monkey-patch."""
    return int(time.time())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enumerate removable worktrees.")
    parser.add_argument("--repo", required=True, help="Repo root (any worktree's path).")
    parser.add_argument("--table", action="store_true", help="Render fixed-width table.")
    parser.add_argument("--count", action="store_true", help="Print total candidate count.")
    parser.add_argument("--head", type=int, default=None, help="With --table: only first N rows.")
    args = parser.parse_args(argv)

    rows = collect(args.repo)
    if args.count:
        print(len(rows))
    elif args.table:
        print(f"Worktrees registered: {len(rows)}")
        out = render_table(rows, _now_epoch(), head=args.head)
        if out:
            print(out)
    else:
        print(json.dumps([asdict(r) for r in rows]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
