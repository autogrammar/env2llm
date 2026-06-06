"""Shared paths for integration tests against the nlp2dsl monorepo."""

from __future__ import annotations

from pathlib import Path

import pytest

NLP2DSL_ROOT = Path(__file__).resolve().parents[1].parent / "nlp2dsl"
EXAMPLES_ROOT = NLP2DSL_ROOT / "examples"
INVOICE_EXAMPLE = EXAMPLES_ROOT / "01-invoice"


@pytest.fixture(scope="session")
def nlp2dsl_root() -> Path:
    return NLP2DSL_ROOT


@pytest.fixture(scope="session")
def invoice_example_dir() -> Path:
    if not INVOICE_EXAMPLE.is_dir():
        pytest.skip("nlp2dsl examples not found (expected ../nlp2dsl/examples)")
    return INVOICE_EXAMPLE
