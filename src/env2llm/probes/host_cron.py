"""Cron parsing and schedule conversion for host probes."""

from __future__ import annotations

import shutil

from env2llm.ir import CronEntryIR

from .host_runtime import TASKINITY_CRON_MARKER, run_cmd


def read_crontab() -> tuple[bool, list[str]]:
    if shutil.which("crontab") is None:
        return False, []
    probe = run_cmd(["crontab", "-l"], timeout=10)
    if probe.returncode != 0:
        return True, []
    lines = [line.strip() for line in probe.stdout.splitlines() if line.strip()]
    return True, lines


def _cron_marker_from_text(text: str, *, current: str = "") -> str:
    if TASKINITY_CRON_MARKER in text:
        return TASKINITY_CRON_MARKER
    return current


def _cron_command_and_marker(command: str, marker: str) -> tuple[str, str]:
    if "#" not in command:
        return command, marker
    cmd_part, comment = command.split("#", 1)
    command = cmd_part.strip()
    comment = comment.strip()
    if TASKINITY_CRON_MARKER in comment:
        return command, TASKINITY_CRON_MARKER
    if comment and not marker:
        return command, comment
    return command, marker


def _parse_scheduled_cron_line(line: str, parts: list[str], marker: str) -> CronEntryIR:
    schedule = " ".join(parts[:5])
    command, marker = _cron_command_and_marker(parts[5], marker)
    return CronEntryIR(
        raw=line,
        schedule=schedule,
        command=command,
        marker=marker,
        enabled=True,
    )


def parse_cron_line(line: str) -> CronEntryIR:
    marker = _cron_marker_from_text(line)
    if line.startswith("#"):
        return CronEntryIR(raw=line, enabled=False, marker=marker)
    parts = line.split(None, 5)
    if len(parts) >= 6:
        return _parse_scheduled_cron_line(line, parts, marker)
    return CronEntryIR(raw=line, command=line, enabled=True, marker=marker)


def cron_probe_state() -> tuple[bool, list[CronEntryIR], bool]:
    cron_ok, cron_lines = read_crontab()
    cron_entries = [parse_cron_line(line) for line in cron_lines]
    taskinity_cron = any(
        entry.enabled and entry.marker == TASKINITY_CRON_MARKER for entry in cron_entries
    )
    return cron_ok, cron_entries, taskinity_cron


def _cron_schedule_from_entry(entry: CronEntryIR, idx: int) -> dict[str, str] | None:
    if not entry.enabled or not entry.schedule:
        return None
    return {
        "id": entry.marker or f"host_cron_{idx}",
        "cron": entry.schedule,
        "task": entry.command or entry.raw,
    }


def cron_entries_to_schedules(entries: list[CronEntryIR]) -> list[dict[str, str]]:
    """Convert enabled cron lines to schedule dicts for SystemMapIR.schedules."""
    out: list[dict[str, str]] = []
    for idx, entry in enumerate(entries):
        schedule = _cron_schedule_from_entry(entry, idx)
        if schedule is not None:
            out.append(schedule)
    return out


# Back-compat for tests importing the private name.
_parse_cron_line = parse_cron_line
