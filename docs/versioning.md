# Versioning strategy

The Multi-Agent PPM Platform follows [Semantic Versioning](https://semver.org/) for public-facing APIs.
We represent versions as `MAJOR.MINOR.PATCH` and publish them through API routes and documentation.

## Version numbers

- **MAJOR**: Breaking changes that require client updates (e.g., renamed endpoints, removed fields,
  response schema changes, or authentication behavior changes).
- **MINOR**: Backwards-compatible features (e.g., new endpoints, optional fields, additional response
  metadata).
- **PATCH**: Backwards-compatible fixes (e.g., bug fixes, documentation corrections, performance
  improvements without API surface changes).

## How we handle change types

| Change type | Examples | Required version bump |
| --- | --- | --- |
| Breaking change | Remove or rename an endpoint, change a required field, alter auth behavior | MAJOR |
| New feature | Add a new endpoint or optional response field | MINOR |
| Fix | Correct a bug or documentation error | PATCH |

## Where versions live

- API version constant: `packages/version.py` (`API_VERSION`).
- API routes: versioned under `/v1` (or higher) across services.
- OpenAPI documentation: namespaced under the same version prefix.

## Breaking changes

Breaking changes must:

1. Be documented in the `CHANGELOG.md` under an **Unreleased → Breaking** section.
2. Bump the major version in `packages/version.py`.
3. Include migration notes in release communications (e.g., updated endpoint paths or payloads).

## Example workflow

1. Add a new optional response field → bump `MINOR` (e.g., `1.1.0`).
2. Fix a validation bug without changing the schema → bump `PATCH` (e.g., `1.1.1`).
3. Remove an endpoint → bump `MAJOR` (e.g., `2.0.0`) and document it in `CHANGELOG.md`.
