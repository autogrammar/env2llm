"""Tests for the non-blocking autoupdate checker."""

from __future__ import annotations

import json
import os
from unittest.mock import patch

from env2llm.autoupdate import (
    _get_cache_dir,
    _is_newer,
    check_for_updates,
)


def test_is_newer_comparison():
    assert _is_newer("0.2.0", "0.1.14") is True
    assert _is_newer("0.1.15", "0.1.14") is True
    assert _is_newer("0.1.14", "0.1.14") is False
    assert _is_newer("0.1.13", "0.1.14") is False
    assert _is_newer("1.0.0a1", "0.9.0") is True


def test_get_cache_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    cache_dir = _get_cache_dir("testpkg")
    assert cache_dir == tmp_path / "testpkg"
    assert cache_dir.is_dir()


def test_check_for_updates_bypasses_in_ci(monkeypatch):
    monkeypatch.setenv("CI", "1")
    with patch("env2llm.autoupdate._spawn_detached_check") as mock_spawn:
        check_for_updates("env2llm")
        mock_spawn.assert_not_called()


def test_check_for_updates_bypasses_on_no_autoupdate(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.setenv("NO_AUTOUPDATE", "1")
    with patch("env2llm.autoupdate._spawn_detached_check") as mock_spawn:
        check_for_updates("env2llm")
        mock_spawn.assert_not_called()


def test_check_for_updates_prints_notice(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("NO_AUTOUPDATE", raising=False)
    monkeypatch.delenv("AUTO_UPGRADE", raising=False)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))

    cache_file = tmp_path / "env2llm" / "update_check.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps({
            "last_check": 9999999999.0,  # fresh check
            "current_version": "0.1.14",
            "latest_version": "0.2.0",
        }),
        encoding="utf-8",
    )

    with patch("importlib.metadata.version", return_value="0.1.14"):
        with patch("env2llm.autoupdate._spawn_detached_check") as mock_spawn:
            check_for_updates("env2llm", ttl_seconds=86400)
            mock_spawn.assert_not_called()

    captured = capsys.readouterr()
    assert "Nowa wersja dostępna: 0.1.14 → 0.2.0" in captured.err
    assert "pip install --upgrade env2llm" in captured.err
