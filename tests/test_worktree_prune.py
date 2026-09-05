"""Regression tests for lib.worktree_prune (lite version).

Pruned from dev-harness-kit's tests/test_worktree_prune.py.
Covers the deterministic age-sort + main-checkout-exclusion contract
that ``bin/worktree-prune.sh`` depends on:

* ``Row.age_days`` handles epoch=0 and future epochs.
* ``_porcelain_blocks`` strips ``refs/heads/`` and tags detached rows.
* ``render_table`` emits a header + one row per input, oldest first;
  ``--head`` slices without a second formatter.
* ``collect`` excludes the main checkout and detached-HEAD worktrees,
  and sorts the remainder oldest-first.
* The CLI (``main``) honors ``--repo`` (required), ``--table``,
  ``--count``, and ``--head``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = ROOT / "lib" / "worktree_prune.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("worktree_prune", SCRIPT)
    assert spec and spec.loader, f"could not load {SCRIPT}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules["worktree_prune"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def wp():
    return _load_module()


# --- Row unit tests (no git) --------------------------------------------


class TestRowAgeDays:
    def test_zero_epoch_returns_zero(self, wp):
        row = wp.Row(path="/p", branch="b", epoch=0, sha="abc")
        assert row.age_days(1_700_000_000) == 0

    def test_normal_epoch(self, wp):
        row = wp.Row(path="/p", branch="b", epoch=1_700_000_000, sha="abc")
        assert row.age_days(1_700_000_000 + 86400 * 5) == 5

    def test_future_epoch_returns_zero(self, wp):
        row = wp.Row(path="/p", branch="b", epoch=1_800_000_000, sha="abc")
        assert row.age_days(1_700_000_000) == 0


# --- porcelain parser ---------------------------------------------------


class TestPorcelainBlocks:
    def test_single_normal_block(self, wp):
        stdout = "worktree /p\nHEAD abc\nbranch refs/heads/feat-x\n\n"
        blocks = list(wp._porcelain_blocks(stdout))
        assert len(blocks) == 1
        assert blocks[0]["worktree"] == "/p"
        assert blocks[0]["branch"] == "feat-x"
        assert blocks[0]["HEAD"] == "abc"

    def test_detached_block(self, wp):
        stdout = "worktree /p\nHEAD abc\ndetached\n\n"
        blocks = list(wp._porcelain_blocks(stdout))
        assert blocks[0].get("detached") == "true"
        assert "branch" not in blocks[0]

    def test_multiple_blocks(self, wp):
        stdout = (
            "worktree /a\nHEAD 111\nbranch refs/heads/a\n\n"
            "worktree /b\nHEAD 222\nbranch refs/heads/b\n\n"
        )
        blocks = list(wp._porcelain_blocks(stdout))
        assert len(blocks) == 2
        assert blocks[0]["branch"] == "a"
        assert blocks[1]["branch"] == "b"

    def test_empty_input(self, wp):
        assert list(wp._porcelain_blocks("")) == []


# --- render_table -------------------------------------------------------


class TestRenderTable:
    def test_empty_returns_empty_string(self, wp):
        assert wp.render_table([], now_epoch=0) == ""

    def test_header_and_rows(self, wp):
        rows = [
            wp.Row(path="/p1", branch="feat-1", epoch=1_700_000_000, sha="abc"),
            wp.Row(path="/p2", branch="feat-2", epoch=1_700_000_100, sha="def"),
        ]
        out = wp.render_table(rows, now_epoch=1_700_000_100 + 86400)
        lines = out.splitlines()
        assert lines[0].startswith("   #  AGE(d)")
        assert "feat-1" in out
        assert "feat-2" in out
        assert "/p1" in out
        assert "/p2" in out

    def test_head_limits_rows(self, wp):
        rows = [
            wp.Row(path="/p1", branch="a", epoch=1, sha="x"),
            wp.Row(path="/p2", branch="b", epoch=2, sha="y"),
            wp.Row(path="/p3", branch="c", epoch=3, sha="z"),
        ]
        out = wp.render_table(rows, now_epoch=10, head=2)
        lines = out.splitlines()
        # header + divider + 2 rows
        assert len(lines) == 4
        assert "/p1" in out and "/p2" in out
        assert "/p3" not in out


# --- collect (integration with real git) --------------------------------


def _init_repo(tmp_path: Path) -> Path:
    """Init a fresh git repo at tmp_path with one commit and two branches."""
    repo = tmp_path / "r"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    (repo / "f").write_text("v1")
    subprocess.run(["git", "-C", str(repo), "add", "f"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
    subprocess.run(["git", "-C", str(repo), "branch", "feat-a"], check=True)
    subprocess.run(["git", "-C", str(repo), "branch", "feat-b"], check=True)
    return repo


class TestCollect:
    def test_excludes_main_checkout(self, tmp_path, wp):
        repo = _init_repo(tmp_path)
        assert wp.collect(str(repo)) == []

    def test_includes_other_worktrees(self, tmp_path, wp):
        repo = _init_repo(tmp_path)
        wt = tmp_path / "wt-feat-a"
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", str(wt), "feat-a"],
            check=True,
        )
        rows = wp.collect(str(repo))
        assert len(rows) == 1
        assert rows[0].branch == "feat-a"
        assert rows[0].epoch > 0
        assert rows[0].sha

    def test_excludes_detached(self, tmp_path, wp):
        repo = _init_repo(tmp_path)
        wt = tmp_path / "wt-detached"
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", "--detach", str(wt)],
            check=True,
        )
        assert wp.collect(str(repo)) == []

    def test_oldest_first_sort(self, tmp_path, wp):
        repo = _init_repo(tmp_path)
        wt_a = tmp_path / "wt-a"
        wt_b = tmp_path / "wt-b"
        # Older branch tip first (feat-a points at init).
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", str(wt_a), "feat-a"],
            check=True,
        )
        # New commit on main.
        (repo / "g").write_text("v2")
        subprocess.run(["git", "-C", str(repo), "add", "g"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-q", "-m", "second"], check=True
        )
        # Move feat-b to the new tip so its epoch is strictly newer.
        subprocess.run(
            ["git", "-C", str(repo), "branch", "-f", "feat-b", "main"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", str(wt_b), "feat-b"],
            check=True,
        )
        rows = wp.collect(str(repo))
        assert len(rows) == 2
        assert rows[0].branch == "feat-a"
        assert rows[1].branch == "feat-b"
        assert rows[0].epoch < rows[1].epoch


# --- CLI mode -----------------------------------------------------------


class TestCLI:
    def test_default_json(self, tmp_path, wp, capsys):
        repo = _init_repo(tmp_path)
        wt = tmp_path / "wt"
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", str(wt), "feat-a"],
            check=True,
        )
        rc = wp.main(["--repo", str(repo)])
        assert rc == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["branch"] == "feat-a"

    def test_count_zero(self, tmp_path, wp, capsys):
        repo = _init_repo(tmp_path)
        rc = wp.main(["--repo", str(repo), "--count"])
        assert rc == 0
        assert capsys.readouterr().out.strip() == "0"

    def test_table(self, tmp_path, wp, capsys):
        repo = _init_repo(tmp_path)
        wt = tmp_path / "wt"
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", str(wt), "feat-a"],
            check=True,
        )
        rc = wp.main(["--repo", str(repo), "--table"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Worktrees registered: 1" in out
        assert "feat-a" in out

    def test_table_with_head(self, tmp_path, wp, capsys):
        repo = _init_repo(tmp_path)
        wt_a = tmp_path / "wt-a"
        wt_b = tmp_path / "wt-b"
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", str(wt_a), "feat-a"],
            check=True,
        )
        (repo / "g").write_text("v2")
        subprocess.run(["git", "-C", str(repo), "add", "g"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-q", "-m", "second"], check=True
        )
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", str(wt_b), "feat-b"],
            check=True,
        )
        rc = wp.main(["--repo", str(repo), "--table", "--head", "1"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Worktrees registered: 2" in out
        assert "feat-a" in out
        assert "feat-b" not in out
