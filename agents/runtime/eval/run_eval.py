"""Runtime evaluation harness for fixture assertions and multi-agent flow manifests."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


class EvaluationError(Exception):
    pass


def _resolve_path(payload: Any, path: str) -> Any:
    current = payload
    for segment in path.split("."):
        if "[" in segment and segment.endswith("]"):
            name, index_str = segment[:-1].split("[")
            if name:
                current = current[name]
            current = current[int(index_str)]
        else:
            current = current[segment]
    return current


def _check_assertion(payload: dict[str, Any], assertion: dict[str, Any]) -> list[str]:
    field = assertion.get("field")
    if not field:
        return ["Assertion missing 'field'."]

    try:
        value = _resolve_path(payload, field)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return [f"Failed to resolve '{field}': {exc}"]

    if "equals" in assertion:
        expected = assertion["equals"]
        if value != expected:
            return [f"Expected {field} == {expected!r}, got {value!r}"]

    if "contains" in assertion:
        expected = assertion["contains"]
        if not isinstance(value, str) or expected not in value:
            return [f"Expected {field} to contain {expected!r}, got {value!r}"]

    return []


def _fixture_output(fixture: dict[str, Any]) -> dict[str, Any]:
    for key in ("actual_output", "output", "response"):
        output = fixture.get(key)
        if isinstance(output, dict):
            return output
    return fixture


def _validate_assertions(
    *,
    evaluation_id: str,
    payload: dict[str, Any],
    assertions: list[dict[str, Any]],
) -> list[str]:
    failures: list[str] = []
    for assertion in assertions:
        failures.extend(
            f"{evaluation_id}: {message}" for message in _check_assertion(payload, assertion)
        )
    return failures


def _run_fixture_evaluation(manifest_path: Path, evaluation: dict[str, Any]) -> list[str]:
    fixture_rel = evaluation.get("fixture")
    if not fixture_rel:
        return [f"{evaluation.get('id', 'unknown')}: Missing fixture path"]

    fixture_path = manifest_path.parent / fixture_rel
    fixture = yaml.safe_load(fixture_path.read_text())
    if not isinstance(fixture, dict):
        return [f"{evaluation.get('id', 'unknown')}: Fixture must be a YAML mapping"]

    failures = _validate_assertions(
        evaluation_id=evaluation["id"],
        payload=fixture,
        assertions=evaluation.get("assertions", []),
    )
    expected_outputs = evaluation.get("expected_outputs", [])
    if expected_outputs:
        failures.extend(
            _validate_assertions(
                evaluation_id=evaluation["id"],
                payload=_fixture_output(fixture),
                assertions=expected_outputs,
            )
        )

    return failures


def _run_multi_agent_flow(manifest_path: Path, flow: dict[str, Any]) -> list[str]:
    flow_id = flow.get("id", "multi-agent-flow")
    failures: list[str] = []
    for index, step in enumerate(flow.get("steps", []), start=1):
        step_id = step.get("id") or f"step-{index}"
        eval_id = f"{flow_id}.{step_id}"
        failures.extend(
            _run_fixture_evaluation(
                manifest_path,
                {
                    "id": eval_id,
                    "fixture": step.get("fixture"),
                    "assertions": step.get("assertions", []),
                    "expected_outputs": step.get("expected_outputs", []),
                },
            )
        )
    return failures


def run_manifest(manifest_path: Path) -> int:
    manifest = yaml.safe_load(manifest_path.read_text())
    if not isinstance(manifest, dict):
        raise EvaluationError("Manifest must be a YAML mapping")

    evaluations = manifest.get("evaluations", [])
    multi_agent_flows = manifest.get("multi_agent_flows", [])
    failures: list[str] = []

    for evaluation in evaluations:
        failures.extend(_run_fixture_evaluation(manifest_path, evaluation))

    for flow in multi_agent_flows:
        failures.extend(_run_multi_agent_flow(manifest_path, flow))

    if failures:
        raise EvaluationError("\n".join(failures))

    return len(evaluations) + len(multi_agent_flows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).with_name("manifest.yaml"),
        help="Path to the evaluation manifest YAML.",
    )
    args = parser.parse_args()

    try:
        total = run_manifest(args.manifest)
    except EvaluationError as exc:
        raise SystemExit(f"Evaluation failed:\n{exc}") from exc

    print(f"{total} evaluations passed.")


if __name__ == "__main__":
    main()
