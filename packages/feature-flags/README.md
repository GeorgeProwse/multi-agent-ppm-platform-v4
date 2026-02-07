# Feature Flags

Feature flag management package for controlling feature availability across the platform.

## MCP rollout flags

Use the following naming conventions to stage MCP rollout safely:

| Scope | Flag name | Example |
| --- | --- | --- |
| Global | `mcp_global_enabled` | `mcp_global_enabled` |
| System | `mcp_system_<system>` | `mcp_system_jira` |
| Project | `mcp_project_<project_id>` | `mcp_project_12345` |

Project flags override system flags, and system flags override the global flag.

## Directory structure

| Folder | Description |
|--------|-------------|
| [src/feature_flags/](./src/feature_flags/) | Core module for feature flag operations |

## Key files

| File | Description |
|------|-------------|
| `src/feature_flags/manager.py` | Feature flag manager implementation |
| `src/feature_flags/__init__.py` | Module init and public exports |
