from __future__ import annotations

import os
from typing import Any

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


class TelemetryPipeline:
    def __init__(self) -> None:
        self._configured = False

    def configure(self) -> None:
        if self._configured:
            return
        connection_string = os.getenv("AZURE_MONITOR_CONNECTION_STRING")
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

        resource = Resource.create({"service.name": "telemetry-service"})
        provider = TracerProvider(resource=resource)
        if otlp_endpoint:
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        if connection_string:
            configure_azure_monitor(connection_string=connection_string)

        self._configured = True

    def tracer(self):
        self.configure()
        return trace.get_tracer("telemetry-service")


PIPELINE = TelemetryPipeline()
