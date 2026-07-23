from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SchemaValidationError(ValueError):
    """Raised when a document does not conform to a project schema."""


class SchemaRegistry:
    def __init__(self, schema_dir: Path):
        self.schema_dir = schema_dir
        self._schemas: dict[str, dict[str, Any]] = {}

    def load(self, name_or_ref: str) -> dict[str, Any]:
        name = name_or_ref.rsplit("/", 1)[-1]
        if not name.endswith(".schema.json"):
            name = f"{name}.schema.json"
        if name not in self._schemas:
            with (self.schema_dir / name).open(encoding="utf-8") as handle:
                self._schemas[name] = json.load(handle)
        return self._schemas[name]

    def validate_file(self, schema_name: str, document_path: Path) -> None:
        with document_path.open(encoding="utf-8") as handle:
            document = json.load(handle)
        self.validate(schema_name, document)

    def validate(self, schema_name: str, document: Any) -> None:
        schema = self.load(schema_name)
        _validate(schema, document, "$", self)


def _validate(schema: dict[str, Any], value: Any, path: str, registry: SchemaRegistry) -> None:
    if "$ref" in schema:
        _validate(registry.load(schema["$ref"]), value, path, registry)
        return

    if "anyOf" in schema:
        errors = []
        for option in schema["anyOf"]:
            try:
                _validate(option, value, path, registry)
                return
            except SchemaValidationError as exc:
                errors.append(str(exc))
        raise SchemaValidationError(f"{path}: did not match any allowed schema: {errors}")

    if "enum" in schema and value not in schema["enum"]:
        raise SchemaValidationError(f"{path}: expected one of {schema['enum']}, got {value!r}")

    expected_type = schema.get("type")
    if expected_type:
        _validate_type(expected_type, value, path)

    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            raise SchemaValidationError(f"{path}: missing required keys {missing}")

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in properties:
                _validate(properties[key], item, f"{path}.{key}", registry)
            elif additional is False:
                raise SchemaValidationError(f"{path}: unexpected key {key!r}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise SchemaValidationError(f"{path}: expected at least {schema['minItems']} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                _validate(item_schema, item, f"{path}[{index}]", registry)

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(value) < min_length:
            raise SchemaValidationError(f"{path}: expected string length >= {min_length}")
        pattern = schema.get("pattern")
        if pattern:
            import re

            if not re.match(pattern, value):
                raise SchemaValidationError(f"{path}: did not match pattern {pattern!r}")


def _validate_type(expected_type: str | list[str], value: Any, path: str) -> None:
    allowed = expected_type if isinstance(expected_type, list) else [expected_type]
    matches = False
    for type_name in allowed:
        if type_name == "object" and isinstance(value, dict):
            matches = True
        elif type_name == "array" and isinstance(value, list):
            matches = True
        elif type_name == "string" and isinstance(value, str):
            matches = True
        elif type_name == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            matches = True
        elif type_name == "integer" and isinstance(value, int) and not isinstance(value, bool):
            matches = True
        elif type_name == "boolean" and isinstance(value, bool):
            matches = True
        elif type_name == "null" and value is None:
            matches = True
    if not matches:
        raise SchemaValidationError(f"{path}: expected type {allowed}, got {type(value).__name__}")
