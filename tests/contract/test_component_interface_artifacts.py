from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema.validators import validator_for


ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = [
    "cli-workspace",
    "system-artifacts",
    "system-harness",
    "operation-directory",
    "component-artifacts",
    "component-harness",
    "component-regression",
    "output-presentation",
]


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(
    loader: UniqueKeyLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def _load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return yaml.load(file, Loader=UniqueKeyLoader)


@pytest.mark.parametrize("component", COMPONENTS)
def test_component_interface_artifacts_are_valid(component: str) -> None:
    component_dir = ROOT / "docs" / component
    semantics_path = component_dir / "semantics.md"
    operations_path = component_dir / "interfaces" / "operations.yaml"

    assert semantics_path.is_file()
    assert operations_path.is_file()

    document = _load_yaml(operations_path)
    assert isinstance(document, dict)
    assert document.get("component") == component

    operations = document.get("operations")
    assert isinstance(operations, dict)
    assert operations

    for operation_id, operation in operations.items():
        assert isinstance(operation_id, str)
        assert isinstance(operation, dict)
        assert operation.get("kind") in {"cli", "function", "http"}
        assert "input" in operation
        assert "output" in operation

        for direction in ("input", "output"):
            schema_ref = operation[direction].get("schema_ref")
            assert isinstance(schema_ref, str)
            assert not Path(schema_ref).is_absolute()

            schema_path = ROOT / schema_ref
            assert schema_path.is_file(), f"{component}.{operation_id} {direction}: {schema_ref}"

            schema = _load_yaml(schema_path)
            assert isinstance(schema, dict)
            assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
            assert schema.get("type") == "object"
            assert schema.get("additionalProperties") is False

            validator_class = validator_for(schema)
            validator_class.check_schema(schema)
