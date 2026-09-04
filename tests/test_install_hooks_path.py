"""Installer must namespace kit hook scripts under .dev-kit/hooks/.

Project-root hooks/ is reserved for the adopting app's own custom hooks
(React/Vue), so bin/install.sh must never write there.
"""

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "bin" / "install.sh"


def _install(tmp_path):
    target = tmp_path / "proj"
    target.mkdir()
    res = subprocess.run(
        ["bash", str(INSTALL), str(target)], capture_output=True, text=True
    )
    assert res.returncode == 0, res.stderr
    return target


def test_hooks_land_under_dev_kit(tmp_path):
    target = _install(tmp_path)
    assert (target / ".dev-kit" / "hooks" / "worktree-guard.sh").is_file()
    assert (target / ".dev-kit" / "hooks" / "hooks.json").is_file()


def test_project_root_hooks_untouched(tmp_path):
    target = _install(tmp_path)
    assert not (target / "hooks").exists()


def test_settings_point_at_namespaced_hooks(tmp_path):
    target = _install(tmp_path)
    for cfg in (".claude/settings.json", ".codex/settings.json"):
        text = (target / cfg).read_text()
        assert ".dev-kit/hooks/hooks.json" in text
        assert "${CLAUDE_PLUGIN_ROOT}/hooks/" not in text
    hooks_json = (target / ".dev-kit" / "hooks" / "hooks.json").read_text()
    assert "${CLAUDE_PLUGIN_ROOT}/hooks/" not in hooks_json
    assert "${CLAUDE_PLUGIN_ROOT}/.dev-kit/hooks/worktree-guard.sh" in hooks_json


def test_kit_own_hooks_dir_has_no_stray_repo_copy():
    """Regression for #12: a botched self-test of install.sh once copied
    the entire kit (skills/, rules/, templates/, tests/, .claude/, etc.)
    into the kit's own hooks/ directory and it was committed by mistake.
    hooks/ must only ever contain the operational hook scripts + their
    shared lib/ helpers + hooks.json + index.md -- nothing install.sh's
    per-project scaffold loop (CLAUDE.md, skills, rules, templates, tests,
    .claude, .codex, .claude-plugin, .codex-plugin) would also copy.
    """
    hooks_dir = REPO / "hooks"
    allowed_dirs = {"lib"}
    for entry in hooks_dir.iterdir():
        if entry.is_dir():
            assert entry.name in allowed_dirs, (
                f"unexpected directory hooks/{entry.name}/ -- "
                "hooks/ must not contain a nested copy of the kit"
            )
    # lib/ itself must only hold the shared hook helpers, not a nested
    # copy of the kit's top-level lib/ (the exact shape of the #12 bug:
    # hooks/lib/lib/execute.py etc.)
    lib_dir = hooks_dir / "lib"
    for entry in lib_dir.iterdir():
        assert entry.is_file(), (
            f"unexpected directory hooks/lib/{entry.name}/ -- "
            "hooks/lib/ must only contain hook helper scripts"
        )
