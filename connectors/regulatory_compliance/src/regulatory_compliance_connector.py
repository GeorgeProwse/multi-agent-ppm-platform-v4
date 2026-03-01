"""
Regulatory Compliance Connector Implementation.

Supports:
- API key authentication
- Reading audit trail records
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_COMMON_SRC = _REPO_ROOT / "packages" / "common" / "src"
if str(_COMMON_SRC) not in sys.path:
    sys.path.insert(0, str(_COMMON_SRC))

from common.bootstrap import ensure_monorepo_paths  # noqa: E402

ensure_monorepo_paths(_REPO_ROOT)

from base_connector import ConnectorCategory, ConnectorConfig  # noqa: E402
from rest_connector import ApiKeyRestConnector  # noqa: E402


class RegulatoryComplianceConnector(ApiKeyRestConnector):
    CONNECTOR_ID = "regulatory_compliance"
    CONNECTOR_NAME = "Regulatory Compliance"
    CONNECTOR_VERSION = "1.0.0"
    CONNECTOR_CATEGORY = ConnectorCategory.COMPLIANCE
    SUPPORTS_WRITE = False

    API_KEY_ENV = "REGULATORY_COMPLIANCE_API_KEY"
    INSTANCE_URL_ENV = "REGULATORY_COMPLIANCE_ENDPOINT"
    API_KEY_HEADER = "Authorization"
    API_KEY_PREFIX = "Bearer"
    AUTH_TEST_ENDPOINT = "/api/v1/audit-trail"
    RESOURCE_PATHS = {
        "audit_trail": {"path": "/api/v1/audit-trail", "items_path": "data"},
    }
    SCHEMA = {
        "audit_trail": {
            "id": "string",
            "regulation": "string",
            "event_type": "string",
            "timestamp": "string",
            "status": "string",
        },
    }

    def __init__(self, config: ConnectorConfig, **kwargs: object) -> None:
        super().__init__(config, **kwargs)
