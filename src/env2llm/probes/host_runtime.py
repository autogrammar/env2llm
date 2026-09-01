"""Shared runtime helpers for host environment probes."""

from __future__ import annotations

import os
import platform
import re
import shutil
import socket
import subprocess
from urllib.request import Request, urlopen

TASKINITY_CRON_MARKER = "taskinity-www-monitor"
DEFAULT_MONITOR_LOG = "/tmp/taskinity-monitor.log"
EXAMPLES_REPORT = "output/examples/comprehensive_report.json"
RELEVANT_PROCESS_RE = re.compile(
    r"(uvicorn|hypervisor|uri2ops|urish|weather|invoice|taskinity|monitor|docker)",
    re.IGNORECASE,
)
AGENT_HTTP_ALWAYS_CHECK = frozenset({8101, 8103, 8110, 8118})


def http_ok(url: str, timeout: float = 2.5) -> tuple[bool, str]:
    try:
        req = Request(url, headers={"User-Agent": "env2llm-host-probe/0.1"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.status == 200, f"status={resp.status}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def tcp_open(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def run_cmd(
    cmd: list[str],
    *,
    timeout: int = 15,
    cwd: object | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def cli_available(name: str) -> bool:
    return shutil.which(name) is not None


def playwright_available() -> bool:
    try:
        import playwright  # noqa: F401

        return True
    except ImportError:
        return False


def uia_available() -> bool:
    if platform.system().lower() != "windows":
        return False
    try:
        import pywinauto  # noqa: F401

        return True
    except ImportError:
        return False


def adb_device() -> bool:
    adb = shutil.which("adb")
    if adb is None:
        return False
    probe = run_cmd([adb, "devices"], timeout=10)
    if probe.returncode != 0:
        return False
    lines = [line for line in probe.stdout.splitlines()[1:] if line.strip()]
    return any("\tdevice" in line for line in lines)


def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    probe = run_cmd(["docker", "info"], timeout=20)
    return probe.returncode == 0


def host_cli_capabilities() -> dict[str, object]:
    return {
        "docker": docker_available(),
        "playwright": playwright_available(),
        "cli_uri": cli_available("uri") or cli_available("urish"),
        "cli_uri3": cli_available("uri3"),
        "cli_hypervisor": cli_available("hypervisor"),
        "cli_touri": cli_available("touri"),
        "cli_uri2flow": cli_available("uri2flow"),
        "cli_nl2uri": cli_available("nl2uri"),
        "curl": cli_available("curl"),
        "adb": adb_device(),
        "uia": uia_available(),
        "openrouter": bool(os.environ.get("OPENROUTER_API_KEY", "").strip()),
    }
