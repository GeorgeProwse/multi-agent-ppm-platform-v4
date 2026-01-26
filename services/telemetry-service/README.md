# Telemetry Service

The telemetry service ingests structured log/metric/trace payloads and emits them to an OpenTelemetry
pipeline. It supports exporting to Azure Monitor via the OTLP collector.

## Contracts

- OpenAPI: `services/telemetry-service/contracts/openapi.yaml`

## Run locally

```bash
python -m tools.component_runner run --type service --name telemetry-service
```

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | unset | OTLP endpoint (collector) |
| `AZURE_MONITOR_CONNECTION_STRING` | unset | Azure Monitor connection string |
| `LOG_LEVEL` | `info` | Logging verbosity |
| `PORT` | `8080` | HTTP port for the service |

## Example request

```bash
curl -X POST http://localhost:8080/telemetry/ingest \
  -H "Content-Type: application/json" \
  -d '{"source": "api-gateway", "type": "log", "payload": {"message": "hello"}}'
```

## Tests

```bash
pytest services/telemetry-service/tests
```
