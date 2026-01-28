from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    AZURE_AVAILABLE = True
except ImportError:
    DefaultAzureCredential = None  # type: ignore
    SecretClient = None  # type: ignore
    AZURE_AVAILABLE = False


@dataclass(frozen=True)
class KeyVaultReference:
    vault_name: str
    secret_name: str
    secret_version: str | None


def _parse_keyvault_reference(value: str) -> KeyVaultReference | None:
    if not value.startswith("keyvault://"):
        return None
    parsed = urlparse(value)
    vault_name = parsed.netloc
    secret_path = parsed.path.lstrip("/")
    if not vault_name or not secret_path:
        raise ValueError(f"Invalid key vault reference: {value}")
    parts = secret_path.split("/")
    secret_name = parts[0]
    secret_version = parts[1] if len(parts) > 1 else None
    return KeyVaultReference(
        vault_name=vault_name,
        secret_name=secret_name,
        secret_version=secret_version,
    )


def resolve_secret(value: Optional[str]) -> Optional[str]:
    """
    Resolve a secret value.

    If the value is a Key Vault reference (keyvault://vault-name/secret-name),
    it will be resolved from Azure Key Vault (requires azure-identity and azure-keyvault-secrets).

    Otherwise, the value is returned as-is.
    """
    if not value:
        return None
    reference = _parse_keyvault_reference(value)
    if not reference:
        return value

    # If Azure SDK is not available, we can't resolve Key Vault references
    if not AZURE_AVAILABLE:
        raise ImportError(
            "Azure SDK is required to resolve Key Vault references. "
            "Install with: pip install azure-identity azure-keyvault-secrets"
        )

    vault_url = f"https://{reference.vault_name}.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    secret = client.get_secret(reference.secret_name, reference.secret_version)
    return secret.value

