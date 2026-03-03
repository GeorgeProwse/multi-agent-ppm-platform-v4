"""
Resource & Capacity Management Agent - Service Classes and Data Models

Contains repository, client, and service classes used by the ResourceCapacityAgent.
"""

import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from typing import Any, cast


class ResourceCapacityRepository:
    def __init__(self, database_url: str | None) -> None:
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.EmployeeProfileRecord = None
        self.CapacityAllocationRecord = None
        if database_url:
            from sqlalchemy import JSON, Float, String, create_engine, select
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

            class Base(DeclarativeBase):
                pass

            class EmployeeProfileRecord(Base):  # type: ignore
                __tablename__ = "employee_profiles"

                employee_id: Mapped[str] = mapped_column(String(128), primary_key=True)
                source_system: Mapped[str] = mapped_column(String(64), default="unknown")
                profile: Mapped[dict[str, Any]] = mapped_column(JSON)
                updated_at: Mapped[str] = mapped_column(String(64))

            class CapacityAllocationRecord(Base):  # type: ignore
                __tablename__ = "capacity_allocations"

                allocation_id: Mapped[str] = mapped_column(String(128), primary_key=True)
                employee_id: Mapped[str] = mapped_column(String(128))
                project_id: Mapped[str] = mapped_column(String(128))
                start_date: Mapped[str] = mapped_column(String(32))
                end_date: Mapped[str] = mapped_column(String(32))
                allocation_percentage: Mapped[float] = mapped_column(Float)
                source_system: Mapped[str] = mapped_column(String(64), default="agent")
                metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

            class ResourceScheduleRecord(Base):  # type: ignore
                __tablename__ = "resource_schedules"

                resource_id: Mapped[str] = mapped_column(String(128), primary_key=True)
                schedule: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
                availability: Mapped[float] = mapped_column(Float, default=1.0)
                updated_at: Mapped[str] = mapped_column(String(64))

            class ResourceForecastRecord(Base):  # type: ignore
                __tablename__ = "resource_forecasts"

                forecast_id: Mapped[str] = mapped_column(String(128), primary_key=True)
                forecast_type: Mapped[str] = mapped_column(String(64))
                payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
                created_at: Mapped[str] = mapped_column(String(64))

            class ResourcePerformanceRecord(Base):  # type: ignore
                __tablename__ = "resource_performance_scores"

                resource_id: Mapped[str] = mapped_column(String(128), primary_key=True)
                score: Mapped[float] = mapped_column(Float, default=0.0)
                metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
                updated_at: Mapped[str] = mapped_column(String(64))

            self.engine = create_engine(database_url)
            Base.metadata.create_all(self.engine)
            self.session_factory = sessionmaker(self.engine)
            self.EmployeeProfileRecord = EmployeeProfileRecord
            self.CapacityAllocationRecord = CapacityAllocationRecord
            self.ResourceScheduleRecord = ResourceScheduleRecord
            self.ResourceForecastRecord = ResourceForecastRecord
            self.ResourcePerformanceRecord = ResourcePerformanceRecord
            self._select = select

    def is_enabled(self) -> bool:
        return self.engine is not None and self.session_factory is not None

    def upsert_employee_profile(self, profile: dict[str, Any]) -> None:
        if not self.is_enabled():
            return
        employee_id = profile.get("employee_id")
        if not employee_id:
            return
        source_system = profile.get("source_system", "unknown")
        updated_at = datetime.now(timezone.utc).isoformat()
        with self.session_factory() as session:  # type: ignore[operator]
            record = session.get(self.EmployeeProfileRecord, employee_id)
            if record:
                record.profile = profile
                record.source_system = source_system
                record.updated_at = updated_at
            else:
                record = self.EmployeeProfileRecord(
                    employee_id=employee_id,
                    source_system=source_system,
                    profile=profile,
                    updated_at=updated_at,
                )
                session.add(record)
            session.commit()

    def upsert_capacity_allocation(self, allocation: dict[str, Any]) -> None:
        if not self.is_enabled():
            return
        allocation_id = allocation.get("allocation_id")
        if not allocation_id:
            return
        with self.session_factory() as session:  # type: ignore[operator]
            record = session.get(self.CapacityAllocationRecord, allocation_id)
            if record:
                record.employee_id = allocation.get("resource_id", "")
                record.project_id = allocation.get("project_id", "")
                record.start_date = allocation.get("start_date", "")
                record.end_date = allocation.get("end_date", "")
                record.allocation_percentage = float(allocation.get("allocation_percentage", 0))
                record.metadata = allocation
            else:
                record = self.CapacityAllocationRecord(
                    allocation_id=allocation_id,
                    employee_id=allocation.get("resource_id", ""),
                    project_id=allocation.get("project_id", ""),
                    start_date=allocation.get("start_date", ""),
                    end_date=allocation.get("end_date", ""),
                    allocation_percentage=float(allocation.get("allocation_percentage", 0)),
                    source_system=allocation.get("source_system", "agent"),
                    metadata=allocation,
                )
                session.add(record)
            session.commit()

    def list_capacity_allocations(self) -> list[dict[str, Any]]:
        if not self.is_enabled():
            return []
        with self.session_factory() as session:  # type: ignore[operator]
            records = session.scalars(self._select(self.CapacityAllocationRecord)).all()
            return [record.metadata for record in records]

    def upsert_resource_schedule(
        self, resource_id: str, schedule: dict[str, Any], availability: float | None = None
    ) -> None:
        if not self.is_enabled():
            return
        updated_at = datetime.now(timezone.utc).isoformat()
        with self.session_factory() as session:  # type: ignore[operator]
            record = session.get(self.ResourceScheduleRecord, resource_id)
            if record:
                record.schedule = schedule
                if availability is not None:
                    record.availability = float(availability)
                record.updated_at = updated_at
            else:
                record = self.ResourceScheduleRecord(
                    resource_id=resource_id,
                    schedule=schedule,
                    availability=float(availability or 0.0),
                    updated_at=updated_at,
                )
                session.add(record)
            session.commit()

    def upsert_forecast(self, forecast_id: str, forecast: dict[str, Any]) -> None:
        if not self.is_enabled():
            return
        forecast_type = forecast.get("type", "capacity")
        created_at = datetime.now(timezone.utc).isoformat()
        with self.session_factory() as session:  # type: ignore[operator]
            record = session.get(self.ResourceForecastRecord, forecast_id)
            if record:
                record.payload = forecast
                record.forecast_type = forecast_type
                record.created_at = created_at
            else:
                record = self.ResourceForecastRecord(
                    forecast_id=forecast_id,
                    forecast_type=forecast_type,
                    payload=forecast,
                    created_at=created_at,
                )
                session.add(record)
            session.commit()

    def upsert_performance_score(
        self, resource_id: str, score: float, metadata: dict[str, Any]
    ) -> None:
        if not self.is_enabled():
            return
        updated_at = datetime.now(timezone.utc).isoformat()
        with self.session_factory() as session:  # type: ignore[operator]
            record = session.get(self.ResourcePerformanceRecord, resource_id)
            if record:
                record.score = float(score)
                record.metadata = metadata
                record.updated_at = updated_at
            else:
                record = self.ResourcePerformanceRecord(
                    resource_id=resource_id,
                    score=float(score),
                    metadata=metadata,
                    updated_at=updated_at,
                )
                session.add(record)
            session.commit()

    def delete_employee_profile(self, employee_id: str) -> None:
        if not self.is_enabled():
            return
        with self.session_factory() as session:  # type: ignore[operator]
            record = session.get(self.EmployeeProfileRecord, employee_id)
            if record:
                session.delete(record)
                session.commit()

    def close(self) -> None:
        if self.engine:
            self.engine.dispose()


class AzureADClient:
    def __init__(self, client_id: str, tenant_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.client_secret = client_secret
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        from msal import ConfidentialClientApplication

        self.app = ConfidentialClientApplication(
            client_id=client_id, authority=self.authority, client_credential=client_secret
        )

    def _get_token(self) -> str:
        token = self.app.acquire_token_for_client(scopes=self.scopes)
        access_token = token.get("access_token")
        if not access_token:
            raise ValueError(f"Failed to acquire Graph token: {token.get('error_description')}")
        return access_token

    def _request(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        access_token = self._get_token()
        import requests

        response = requests.get(
            f"https://graph.microsoft.com/v1.0{path}",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def list_users(self) -> list[dict[str, Any]]:
        response = self._request(
            "/users",
            params={"$select": "id,displayName,mail,jobTitle,department,employeeId"},
        )
        return cast(list[dict[str, Any]], response.get("value", []))

    def list_user_skills(self, user_id: str) -> list[str]:
        response = self._request(f"/users/{user_id}/profile/skills")
        return [skill.get("displayName") for skill in response.get("value", []) if skill]

    def get_calendar_availability(
        self, user_id: str, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        response = self._request(
            f"/users/{user_id}/calendarView",
            params={
                "startDateTime": start.isoformat(),
                "endDateTime": end.isoformat(),
                "$select": "start,end,showAs",
            },
        )
        return cast(list[dict[str, Any]], response.get("value", []))


class EmbeddingClient:
    def __init__(self, endpoint: str | None, api_key: str | None, deployment: str | None) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.deployment)

    def get_embedding(self, text: str) -> list[float]:
        if self.is_configured():
            import requests

            response = requests.post(
                f"{self.endpoint}/openai/deployments/{self.deployment}/embeddings",
                headers={
                    "api-key": cast(str, self.api_key),
                    "Content-Type": "application/json",
                },
                params={"api-version": "2023-05-15"},
                json={"input": text},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return cast(list[float], data["data"][0]["embedding"])
        return self._fallback_embedding(text)

    @staticmethod
    def _fallback_embedding(text: str, dims: int = 64) -> list[float]:
        vector = [0.0] * dims
        for token in text.lower().split():
            token_hash = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            index = token_hash % dims
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class AzureSearchClient:
    def __init__(self, endpoint: str | None, api_key: str | None, index_name: str | None) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.index_name = index_name

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.index_name)

    def upload_documents(self, documents: list[dict[str, Any]]) -> None:
        if not self.is_configured():
            return
        import requests

        response = requests.post(
            f"{self.endpoint}/indexes/{self.index_name}/docs/index",
            headers={"api-key": cast(str, self.api_key), "Content-Type": "application/json"},
            params={"api-version": "2023-07-01-Preview"},
            json={"value": documents},
            timeout=30,
        )
        response.raise_for_status()

    def query_documents(
        self, query_vector: list[float], query_text: str, top_k: int = 5
    ) -> list[dict[str, Any]]:
        if not self.is_configured():
            return []
        import requests

        response = requests.post(
            f"{self.endpoint}/indexes/{self.index_name}/docs/search",
            headers={"api-key": cast(str, self.api_key), "Content-Type": "application/json"},
            params={"api-version": "2023-07-01-Preview"},
            json={
                "search": query_text,
                "vectorQueries": [{"vector": query_vector, "fields": "embedding", "k": top_k}],
                "select": "resource_id,skills,role,availability,cost_rate",
            },
            timeout=30,
        )
        response.raise_for_status()
        return cast(list[dict[str, Any]], response.json().get("value", []))


class TimeSeriesForecaster:
    def __init__(
        self, *, automl_endpoint: str | None = None, automl_api_key: str | None = None
    ) -> None:
        self.automl_endpoint = automl_endpoint
        self.automl_api_key = automl_api_key

    def forecast(self, series: list[float], periods: int) -> list[float]:
        if not series:
            return [0.0 for _ in range(periods)]
        automl_forecast = self._forecast_with_automl(series, periods)
        if automl_forecast is not None:
            return automl_forecast
        prophet_forecast = self._forecast_with_prophet(series, periods)
        if prophet_forecast is not None:
            return prophet_forecast
        return self._linear_forecast(series, periods)

    def _linear_forecast(self, series: list[float], periods: int) -> list[float]:
        if len(series) < 2:
            return [series[0] for _ in range(periods)]
        x_values = list(range(len(series)))
        x_mean = sum(x_values) / len(x_values)
        y_mean = sum(series) / len(series)
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, series))
        denominator = sum((x - x_mean) ** 2 for x in x_values) or 1.0
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        start = len(series)
        return [slope * (start + i) + intercept for i in range(periods)]

    def _forecast_with_prophet(self, series: list[float], periods: int) -> list[float] | None:
        try:
            import pandas as pd
            from prophet import Prophet
        except (
            ImportError,
            ModuleNotFoundError,
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ):
            return None
        if len(series) < 2:
            return None
        start_date = datetime.now(timezone.utc).date()
        history = [
            {"ds": start_date + timedelta(days=index), "y": value}
            for index, value in enumerate(series)
        ]
        df = pd.DataFrame(history)
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=periods, freq="D")
        forecast = model.predict(future)
        forecast_values = forecast.tail(periods)["yhat"].tolist()
        return [float(value) for value in forecast_values]

    def _forecast_with_automl(self, series: list[float], periods: int) -> list[float] | None:
        if not self.automl_endpoint or not self.automl_api_key:
            return None
        try:
            import requests

            response = requests.post(
                f"{self.automl_endpoint}/forecast",
                headers={
                    "Authorization": f"Bearer {self.automl_api_key}",
                    "Content-Type": "application/json",
                },
                json={"series": series, "horizon": periods},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            forecasts = data.get("forecast")
            if isinstance(forecasts, list):
                return [float(value) for value in forecasts]
        except (
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ):
            return None
        return None


class AIMLForecastClient:
    def __init__(self, endpoint: str | None, api_key: str | None) -> None:
        self.endpoint = endpoint
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key)

    def train_model(
        self,
        model_name: str,
        series: list[float],
        horizon: int,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if not self.is_configured():
            return None
        import requests

        response = requests.post(
            f"{self.endpoint}/forecasting/train",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model_name": model_name,
                "series": series,
                "horizon": horizon,
                "metadata": metadata or {},
            },
            timeout=30,
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    def forecast(self, model_name: str, series: list[float], horizon: int) -> list[float] | None:
        if not self.is_configured():
            return None
        import requests

        response = requests.post(
            f"{self.endpoint}/forecasting/predict",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model_name": model_name, "series": series, "horizon": horizon},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        forecast = payload.get("forecast")
        if isinstance(forecast, list):
            return [float(value) for value in forecast]
        return None


class EventPublisher:
    def __init__(self, connection_string: str | None, queue_name: str | None) -> None:
        self.connection_string = connection_string
        self.queue_name = queue_name

    def is_configured(self) -> bool:
        return bool(self.connection_string and self.queue_name)

    def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        if not self.is_configured():
            return
        from azure.servicebus import ServiceBusClient, ServiceBusMessage

        with ServiceBusClient.from_connection_string(cast(str, self.connection_string)) as client:
            sender = client.get_queue_sender(queue_name=cast(str, self.queue_name))
            with sender:
                message = ServiceBusMessage(json.dumps({"event": event_name, "payload": payload}))
                sender.send_messages(message)


class NotificationService:
    def __init__(
        self,
        graph_client: AzureADClient | None,
        *,
        acs_connection_string: str | None = None,
        acs_sender: str | None = None,
    ) -> None:
        self.graph_client = graph_client
        self.acs_connection_string = acs_connection_string
        self.acs_sender = acs_sender

    def send_email(self, recipient: str, subject: str, content: str) -> None:
        if self.graph_client:
            access_token = self.graph_client._get_token()
            import requests

            response = requests.post(
                "https://graph.microsoft.com/v1.0/users/me/sendMail",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "message": {
                        "subject": subject,
                        "body": {"contentType": "Text", "content": content},
                        "toRecipients": [{"emailAddress": {"address": recipient}}],
                    }
                },
                timeout=30,
            )
            response.raise_for_status()
            return
        if self.acs_connection_string and self.acs_sender:
            try:
                from azure.communication.email import EmailClient
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                KeyError,
                TypeError,
                RuntimeError,
                OSError,
            ) as exc:
                raise RuntimeError(
                    "Azure Communication Services email client unavailable."
                ) from exc
            client = EmailClient.from_connection_string(self.acs_connection_string)
            poller = client.begin_send(
                {
                    "senderAddress": self.acs_sender,
                    "recipients": {"to": [{"address": recipient}]},
                    "content": {"subject": subject, "plainText": content},
                }
            )
            poller.result()
            return
        raise RuntimeError("No notification client configured")


class LearningManagementClient:
    def __init__(
        self,
        moodle_endpoint: str | None,
        moodle_token: str | None,
        coursera_endpoint: str | None,
        coursera_token: str | None,
        training_records: list[dict[str, Any]] | None = None,
    ) -> None:
        self.moodle_endpoint = moodle_endpoint
        self.moodle_token = moodle_token
        self.coursera_endpoint = coursera_endpoint
        self.coursera_token = coursera_token
        self.training_records = training_records or []

    def is_configured(self) -> bool:
        return bool(
            self.training_records
            or (self.moodle_endpoint and self.moodle_token)
            or (self.coursera_endpoint and self.coursera_token)
        )

    def fetch_training_records(self, resource_ids: list[str]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        if self.training_records:
            record_index = {record.get("resource_id"): record for record in self.training_records}
            for resource_id in resource_ids:
                if resource_id in record_index:
                    records.append(record_index[resource_id])
            return records
        if self.moodle_endpoint and self.moodle_token:
            records.extend(self._fetch_moodle_records(resource_ids))
        if self.coursera_endpoint and self.coursera_token:
            records.extend(self._fetch_coursera_records(resource_ids))
        return records

    def _fetch_moodle_records(self, resource_ids: list[str]) -> list[dict[str, Any]]:
        import requests

        response = requests.get(
            f"{self.moodle_endpoint}/api/training-records",
            headers={"Authorization": f"Bearer {self.moodle_token}"},
            params={"resource_ids": ",".join(resource_ids)},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return cast(list[dict[str, Any]], payload.get("records", []))

    def _fetch_coursera_records(self, resource_ids: list[str]) -> list[dict[str, Any]]:
        import requests

        response = requests.get(
            f"{self.coursera_endpoint}/api/training-records",
            headers={"Authorization": f"Bearer {self.coursera_token}"},
            params={"resource_ids": ",".join(resource_ids)},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return cast(list[dict[str, Any]], payload.get("records", []))


class ApprovalWorkflowClient:
    def __init__(self, approval_agent: Any | None, event_bus: Any | None) -> None:
        self.approval_agent = approval_agent
        self.event_bus = event_bus

    async def request_approval(
        self,
        request: dict[str, Any],
        *,
        tenant_id: str,
        correlation_id: str,
        approver_hint: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "request_type": "resource_change",
            "request_id": request.get("request_id"),
            "requester": request.get("requested_by", "unknown"),
            "details": {
                "project_id": request.get("project_id"),
                "required_skills": request.get("required_skills", []),
                "start_date": request.get("start_date"),
                "end_date": request.get("end_date"),
                "effort": request.get("effort", 1.0),
                "approver_hint": approver_hint,
            },
            "context": {"tenant_id": tenant_id, "correlation_id": correlation_id},
        }
        if self.approval_agent:
            return await self.approval_agent.process(payload)
        if self.event_bus:
            await self.event_bus.publish("approval.requested", payload)
        return {"status": "pending", "approval_id": None, "approvers": []}

    async def record_decision(
        self,
        approval_id: str,
        *,
        decision: str,
        approver_id: str,
        comments: str | None,
        tenant_id: str,
        correlation_id: str,
    ) -> dict[str, Any]:
        payload = {
            "approval_id": approval_id,
            "decision": decision,
            "approver_id": approver_id,
            "comments": comments,
            "context": {"tenant_id": tenant_id, "correlation_id": correlation_id},
        }
        if self.approval_agent:
            return await self.approval_agent.process(payload)
        if self.event_bus:
            await self.event_bus.publish("approval.decision", payload)
        return {"status": decision}


class SimpleAnalyticsClient:
    def __init__(self) -> None:
        self.metrics: list[tuple[str, float, dict[str, Any]]] = []

    def record_metric(
        self, name: str, value: float, metadata: dict[str, Any] | None = None
    ) -> None:
        self.metrics.append((name, value, metadata or {}))
