# Key Vault Module

## Rotation webhook configuration

This module supports optional webhook notifications for Key Vault secret expiry events.

- `enable_rotation_webhook` (optional, default: `false`):
  - When `false`, webhook receiver configuration and the secret expiry Event Grid subscription are not created.
  - When `true`, webhook receiver configuration and the secret expiry Event Grid subscription are created.
- `rotation_webhook_url` (conditionally required):
  - Optional when `enable_rotation_webhook = false`.
  - Required when `enable_rotation_webhook = true`.
  - Must be a valid HTTPS URL when provided.

If `enable_rotation_webhook` is `true` and `rotation_webhook_url` is empty, Terraform fails with:

`rotation_webhook_url must be provided when enable_rotation_webhook is true.`
