from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from workflow_storage import WorkflowStore

from jsonschema import Draft202012Validator, FormatChecker


def load_definition(path: Path, schema_path: Path) -> dict[str, Any]:
    definition = yaml.safe_load(path.read_text())
    schema = yaml.safe_load(schema_path.read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(definition), key=lambda err: err.path)
    if errors:
        formatted = "; ".join(error.message for error in errors)
        raise ValueError(f"Workflow definition invalid: {formatted}")
    return definition


def seed_definitions(store: WorkflowStore, definitions_dir: Path, schema_path: Path) -> None:
    if not definitions_dir.exists():
        return
    for definition_path in definitions_dir.glob("*.workflow.yaml"):
        workflow_id = definition_path.stem.replace(".workflow", "")
        if store.get_definition(workflow_id):
            continue
        definition = load_definition(definition_path, schema_path)
        store.upsert_definition(workflow_id, definition)
