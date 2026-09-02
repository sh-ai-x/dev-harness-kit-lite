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
