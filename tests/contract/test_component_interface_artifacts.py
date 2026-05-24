from __future__ import annotations

from pathlib import Path
from typing import Any
import re

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
BUILTIN_TYPES = {"Path", "str", "int", "bool", "None", "list", "dict"}


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


def _schema_ref_target(schema_ref: str) -> tuple[Path, str]:
    path_text, _, fragment = schema_ref.partition("#")
    assert not Path(path_text).is_absolute()
    assert fragment.startswith("/$defs/")
    return ROOT / path_text, fragment.removeprefix("/$defs/")


def _custom_signature_types(signature: str) -> set[str]:
    names = set(re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", signature))
    return names - BUILTIN_TYPES


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
        kind = operation.get("kind")
        assert kind in {"cli", "function", "http"}

        schema_refs = operation.get("schema_refs")
        assert isinstance(schema_refs, dict)
        assert schema_refs

        if kind == "function":
            signature = operation.get("signature")
            assert isinstance(signature, str)
            assert re.fullmatch(r"\w+\(.+\) -> [A-Za-z_][A-Za-z0-9_]*( \| None)?", signature)
            assert set(schema_refs) == _custom_signature_types(signature)

        if kind == "cli":
            assert isinstance(operation.get("command"), str)

        for type_name, schema_ref in schema_refs.items():
            assert isinstance(type_name, str)
            assert isinstance(schema_ref, str)
            schema_path, definition_name = _schema_ref_target(schema_ref)
            assert type_name == definition_name

            assert schema_path.is_file(), f"{component}.{operation_id}: {schema_ref}"

            schema = _load_yaml(schema_path)
            assert isinstance(schema, dict)
            assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
            assert schema.get("type") == "object"
            assert schema.get("additionalProperties") is False
            assert isinstance(schema.get("$defs"), dict)
            assert definition_name in schema["$defs"]

            validator_class = validator_for(schema)
            validator_class.check_schema(schema)

            definition = schema["$defs"][definition_name]
            assert definition.get("type") == "object"
            assert definition.get("additionalProperties") is False
