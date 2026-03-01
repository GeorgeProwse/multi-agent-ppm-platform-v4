# Supported Systems

## Purpose

List connector coverage and maturity based on the current connector registry and packaged connector assets.

## Status definitions

- **production**: Certified connector with automated tests and runtime support.
- **beta**: Functional connector package with runtime support and in-progress certification.

## Connector coverage

The full list of supported systems, their categories, and MCP/REST coverage is
derived from connector manifests.  View it via the generated registry:

```bash
python -c "import json; [print(f\"{c['id']:30s} {c['category']:15s} {c['status']}\" ) for c in json.load(open('connectors/registry/connectors.json'))]"
```

To check which systems have MCP counterparts, look for connectors whose manifest
contains `protocol: mcp` and compare by `system` field.

## Registry status (runtime-ready)

The authoritative registry list lives in `connectors/registry/connectors.json` and is
generated from connector manifests by `connectors/registry/generate.py`.  Do not edit
the JSON file by hand — regenerate it instead:

```bash
python connectors/registry/generate.py
```

## Verification steps

- View the registry:
  ```bash
  cat connectors/registry/connectors.json
  ```
- Check for connector manifests:
  ```bash
  ls connectors/*/manifest.yaml
  ```

## Implementation status

- **Implemented:** Connector registry now includes every packaged connector.
- **Implemented:** All listed connector packages include manifests and runtime mappings.

## Related docs

- [Connector Overview](overview.md)
- [Connector Certification](certification.md)
- [Connector Data Mapping](data-mapping.md)
- [MCP Coverage Matrix](mcp-coverage-matrix.md)
