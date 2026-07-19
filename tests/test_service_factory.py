"""Contract tests for the public env2llm service factory."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from env2llm.service import (
    SERVICE_DESCRIPTOR_V1,
    SERVICE_FACTORY_ERROR_V1,
    SERVICE_FACTORY_REQUEST_V1,
    RegistryServiceFactory,
    ServiceFactoryError,
    ServiceFactoryRequest,
    UnknownServiceKindError,
    service_contract_schema,
)

ROOT = Path(__file__).resolve().parents[1]


def test_request_and_descriptor_are_versioned_and_stably_hashed(tmp_path) -> None:
    request = ServiceFactoryRequest(
        project_dir=tmp_path,
        project_id="demo",
        probe_desktop=False,
        mqtt=False,
    )
    same = ServiceFactoryRequest.from_dict(request.to_dict())
    factory = RegistryServiceFactory()

    first = factory.create(request)
    second = factory.create(same)

    assert request.schema == SERVICE_FACTORY_REQUEST_V1
    assert request.request_hash == same.request_hash
    assert first.service is second.service
    assert first.descriptor.schema == SERVICE_DESCRIPTOR_V1
    assert first.descriptor.request_hash == request.request_hash
    assert first.descriptor.descriptor_hash == second.descriptor.descriptor_hash
    assert len(first.descriptor.descriptor_hash) == 64


def test_unknown_service_kind_is_a_typed_error(tmp_path) -> None:
    factory = RegistryServiceFactory()
    with pytest.raises(UnknownServiceKindError) as caught:
        factory.create(ServiceFactoryRequest(project_dir=tmp_path, kind="vector-db"))

    payload = caught.value.to_dict()
    assert payload == {
        "schema": SERVICE_FACTORY_ERROR_V1,
        "ok": False,
        "code": "unknown_service_kind",
        "kind": "vector-db",
        "message": "unknown env2llm service kind 'vector-db' (known: registry)",
    }


@pytest.mark.parametrize("field", ["probe_desktop", "mqtt", "merge_existing"])
def test_malformed_boolean_fields_fail_closed(tmp_path, field) -> None:
    payload = {"project_dir": str(tmp_path), field: "false"}
    with pytest.raises(ServiceFactoryError, match=field):
        ServiceFactoryRequest.from_dict(payload)


def test_unknown_fields_and_tampered_hash_fail_closed(tmp_path) -> None:
    with pytest.raises(ServiceFactoryError, match="unknown.*unexpected"):
        ServiceFactoryRequest.from_dict(
            {"project_dir": str(tmp_path), "unexpected": "LLM guess"}
        )

    request = ServiceFactoryRequest(project_dir=tmp_path)
    payload = request.to_dict()
    payload["request_hash"] = "0" * 64
    with pytest.raises(ServiceFactoryError, match="request_hash"):
        ServiceFactoryRequest.from_dict(payload)


@pytest.mark.parametrize(
    "schema_id",
    [SERVICE_FACTORY_REQUEST_V1, SERVICE_DESCRIPTOR_V1, SERVICE_FACTORY_ERROR_V1],
)
def test_public_contract_schemas_are_packaged(schema_id) -> None:
    schema = service_contract_schema(schema_id)
    assert schema["properties"]["schema"]["const"] == schema_id


def test_integrators_do_not_import_the_private_factory() -> None:
    offenders: list[str] = []
    for path in (ROOT / "src/env2llm").rglob("*.py"):
        if path.name == "_service_factory.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "env2llm.integrators._service_factory"
            ):
                offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []
