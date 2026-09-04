"""test_proposal_skill.py — regression for lib/render_proposal_html.py.

Ported (skill + lib) from the full dev-kit's proposal skill. This file is
a proportionate smoke/regression subset for dev-kit-lite, not a line-for-
line port of dev-kit's 1500-line suite: it covers parsing, HTML escaping,
status-bucket routing, and the CLI render/list paths — the behaviors this
kit's users actually exercise from `/dev-kit-lite:proposal`.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml", reason="PyYAML is required by the proposal skill")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from lib.render_proposal_html import (  # noqa: E402
    bucket_for_status,
    parse_proposal_yaml,
    render,
)

MINIMAL_YAML = """
title: Minimal Proposal
status: draft
date: 2026-09-05
tags: [smoke]
sections:
  - title: TL;DR
    body: |
      Plain **markdown-lite** body.
"""

FULL_YAML = """
title: Full Proposal
status: accepted
date: 2026-09-05
tags: [smoke, full]
before:
  summary: |
    No smoke coverage existed for the ported renderer.
  evidence:
    - 'manual verification only'
after:
  summary: |
    A pytest file exercises parse + render + CLI.
  files:
    - path: tests/test_proposal_skill.py
      change: 'new test file'
pros:
  - 'Confirms the port renders'
cons:
  - 'Not exhaustive'
limitations:
  - 'Does not cover --migrate'
sections:
  - title: TL;DR
    body: |
      Full-shape body with a malicious title test elsewhere.
"""


def test_parse_minimal_yaml_has_no_before_after():
    p = parse_proposal_yaml(MINIMAL_YAML)
    assert p.title == "Minimal Proposal"
    assert p.status == "draft"
    assert p.before is None
    assert p.after is None
    assert len(p.sections) == 1


def test_parse_full_yaml_has_before_after_and_lists():
    p = parse_proposal_yaml(FULL_YAML)
    assert p.before is not None
    assert p.after is not None
    assert p.pros == ["Confirms the port renders"]
    assert p.cons == ["Not exhaustive"]
    assert p.limitations == ["Does not cover --migrate"]


@pytest.mark.parametrize(
    "status,expected_bucket",
    [
        ("draft", "review"),
        ("design-discussion", "review"),
        ("ready-for-review", "review"),
        ("accepted", "accepted"),
        ("rejected", "rejected"),
        ("superseded", "rejected"),
        ("not-a-real-status", "review"),  # unknown falls back to review
    ],
)
def test_bucket_for_status(status, expected_bucket):
    assert bucket_for_status(status) == expected_bucket


def test_render_escapes_script_in_title():
    malicious = MINIMAL_YAML.replace(
        "title: Minimal Proposal", "title: <script>alert(1)</script>"
    )
    p = parse_proposal_yaml(malicious)
    html_out = render(p)
    assert "<script>alert(1)</script>" not in html_out
    assert "&lt;script&gt;" in html_out


def test_render_no_fields_emits_no_before_after_section():
    p = parse_proposal_yaml(MINIMAL_YAML)
    html_out = render(p)
    assert 'class="ba-grid"' not in html_out
    assert 'class="pros-list"' not in html_out
    assert 'class="cons-list"' not in html_out


def test_render_command_prefix_is_dev_kit_lite():
    p = parse_proposal_yaml(MINIMAL_YAML)
    html_out = render(p)
    assert "/dev-kit-lite:proposal" in html_out
    assert "/dev-kit:proposal" not in html_out


def test_cli_render_and_list_roundtrip(tmp_path):
    proposals_dir = tmp_path / "docs" / "proposals" / "review" / "smoke"
    proposals_dir.mkdir(parents=True)
    (proposals_dir / "sample.yaml").write_text(MINIMAL_YAML)

    render_res = subprocess.run(
        [sys.executable, "-m", "lib.render_proposal_html", "smoke/sample",
         "--project-root", str(tmp_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert render_res.returncode == 0, render_res.stderr
    assert (proposals_dir / "sample.html").exists()

    list_res = subprocess.run(
        [sys.executable, "-m", "lib.render_proposal_html", "--list",
         "--project-root", str(tmp_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert list_res.returncode == 0, list_res.stderr
    assert "review/smoke/sample" in list_res.stdout
