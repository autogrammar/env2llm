# Ticket 002: Add non-blocking autoupdate notice and fix Python 3.10 compatibility

- **ID**: ticket-002
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-10-11

## Goal and scope

1. Introduce non-blocking PyPI update notice checking in `src/env2llm/autoupdate.py` and hook into `env2llm.cli:main`.
2. Verify Python 3.10 and 3.13 compatibility with locked dependencies.
3. Add unit tests in `tests/test_autoupdate.py`.

## Acceptance criteria

- [x] AC-01: Non-blocking background autoupdate checker in `src/env2llm/autoupdate.py`.
- [x] AC-02: Hook `check_for_updates("env2llm")` in `src/env2llm/cli.py`.
- [x] AC-03: Comprehensive unit tests in `tests/test_autoupdate.py` passing on supported Python versions.
- [x] AC-04: Governance checks pass cleanly with 0 errors and 0 warnings.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
