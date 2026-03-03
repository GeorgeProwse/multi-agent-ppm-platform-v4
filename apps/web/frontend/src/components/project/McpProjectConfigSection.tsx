/**
 * McpProjectConfigSection - Inline MCP configuration panel shown on connector cards
 * that use the MCP transport.
 */

import { useEffect, useMemo, useState, type ChangeEvent } from 'react';
import { useConnectorStore } from '@/store/connectors';
import styles from '../connectors/ConnectorGallery.module.css';
import { MCP_SERVER_OPTIONS, type McpProjectConfigSectionProps } from './projectConnectorTypes';

export function McpProjectConfigSection({
  connector,
  canManage,
  projectId,
  onToggleMcpEnabled,
  onUpdateMcpToolMap,
}: McpProjectConfigSectionProps) {
  const { mcpToolsBySystem, mcpToolsLoading, mcpToolsError, fetchMcpTools } = useConnectorStore();
  const mcpFeatureEnabled = connector.mcp_feature_enabled ?? true;
  const [mcpEnabled, setMcpEnabled] = useState(connector.mcp_enabled ?? true);
  const [mcpServerId, setMcpServerId] = useState(connector.mcp_server_id ?? '');
  const [mcpServerUrl, setMcpServerUrl] = useState(connector.mcp_server_url ?? '');
  const [toolMap, setToolMap] = useState<Record<string, string>>(() =>
    Object.entries(connector.mcp_tool_map ?? {}).reduce<Record<string, string>>(
      (acc, [operation, tool]) => {
        acc[operation] = String(tool ?? '');
        return acc;
      },
      {}
    )
  );
  const [saving, setSaving] = useState(false);
  const operations = useMemo(() => {
    if (connector.supported_operations.length) {
      return connector.supported_operations;
    }
    const mapped = Object.keys(toolMap);
    return mapped.length ? mapped : ['projects.read', 'projects.write'];
  }, [connector.supported_operations, toolMap]);

  useEffect(() => {
    setMcpEnabled(connector.mcp_enabled ?? true);
    setMcpServerId(connector.mcp_server_id ?? '');
    setMcpServerUrl(connector.mcp_server_url ?? '');
    setToolMap(
      Object.entries(connector.mcp_tool_map ?? {}).reduce<Record<string, string>>(
        (acc, [operation, tool]) => {
          acc[operation] = String(tool ?? '');
          return acc;
        },
        {}
      )
    );
  }, [
    connector.mcp_enabled,
    connector.mcp_tool_map,
    connector.mcp_server_id,
    connector.mcp_server_url,
  ]);

  useEffect(() => {
    if (!mcpFeatureEnabled) return;
    fetchMcpTools(connector.system);
  }, [connector.system, fetchMcpTools, mcpFeatureEnabled]);

  const buildToolMapPayload = () =>
    Object.entries(toolMap).reduce<Record<string, string>>((acc, [operation, tool]) => {
      const trimmed = tool.trim();
      if (trimmed) {
        acc[operation] = trimmed;
      }
      return acc;
    }, {});

  const handleToggle = async (event: ChangeEvent<HTMLInputElement>) => {
    if (!canManage || !mcpFeatureEnabled) return;
    const nextEnabled = event.target.checked;
    setMcpEnabled(nextEnabled);
    await onToggleMcpEnabled(projectId, connector.connector_id, nextEnabled, {
      mcp_server_id: mcpServerId,
      mcp_server_url: mcpServerUrl,
      mcp_tool_map: buildToolMapPayload(),
    });
  };

  const handleToolChange = (operation: string, value: string) => {
    setToolMap((prev) => ({ ...prev, [operation]: value }));
  };

  const handleSave = async () => {
    if (!canManage) return;
    setSaving(true);
    const payload = buildToolMapPayload();
    try {
      await onUpdateMcpToolMap(projectId, connector.connector_id, payload, {
        mcp_server_id: mcpServerId,
        mcp_server_url: mcpServerUrl,
      });
    } finally {
      setSaving(false);
    }
  };

  const toolCatalog = mcpToolsBySystem[connector.system] ?? [];
  const toolCatalogNames = toolCatalog.map((tool) => tool.name);
  const canToggleMcp = canManage && mcpFeatureEnabled && (mcpEnabled || Boolean(mcpServerUrl));

  return (
    <div className={styles.mcpConfigSection}>
      <div className={styles.mcpConfigHeader}>
        <div>
          <div className={styles.mcpConfigTitle}>Project MCP Configuration</div>
          <p className={styles.mcpConfigHint}>
            Bind project-level operations to MCP tools for this connector.
          </p>
        </div>
        <label className={styles.mcpToggle}>
          <span>Enable MCP for this project</span>
          <span className={styles.mcpToggleSwitch}>
            <input
              type="checkbox"
              checked={mcpEnabled}
              onChange={handleToggle}
              disabled={!canToggleMcp}
              aria-label={`Enable MCP for ${connector.name}`}
            />
            <span className={styles.toggleSlider}></span>
          </span>
        </label>
      </div>
      {!mcpFeatureEnabled && (
        <span className={styles.fieldHint}>
          MCP is disabled by feature flag for this system.
        </span>
      )}

      <div className={styles.formField}>
        <label className={styles.fieldLabel}>MCP Server</label>
        <select
          className={styles.fieldSelect}
          value={mcpServerId}
          onChange={(event) => setMcpServerId(event.target.value)}
          disabled={!canManage}
        >
          <option value="">Select a server</option>
          {MCP_SERVER_OPTIONS.map((option) => (
            <option key={option.id} value={option.id}>
              {option.label}
            </option>
          ))}
          {connector.mcp_server_id &&
            !MCP_SERVER_OPTIONS.some((option) => option.id === connector.mcp_server_id) && (
              <option value={connector.mcp_server_id}>
                Current: {connector.mcp_server_id}
              </option>
            )}
        </select>
      </div>

      <div className={styles.formField}>
        <label className={styles.fieldLabel}>MCP Server URL</label>
        <input
          type="url"
          className={styles.fieldInput}
          placeholder="https://mcp.example.com"
          value={mcpServerUrl}
          onChange={(event) => setMcpServerUrl(event.target.value)}
          disabled={!canManage}
        />
      </div>

      <div className={styles.mcpToolMap}>
        {operations.map((operation) => (
          <div key={operation} className={styles.mcpToolRow}>
            <label className={styles.mcpToolLabel} htmlFor={`${connector.connector_id}-${operation}`}>
              {operation}
            </label>
            <input
              id={`${connector.connector_id}-${operation}`}
              className={styles.mcpToolInput}
              type="text"
              value={toolMap[operation] ?? ''}
              onChange={(event) => handleToolChange(operation, event.target.value)}
              placeholder="e.g., portfolio.read"
              disabled={!canManage}
              list={`${connector.connector_id}-mcp-tool-catalog`}
            />
          </div>
        ))}
      </div>
      <datalist id={`${connector.connector_id}-mcp-tool-catalog`}>
        {toolCatalogNames.map((tool) => (
          <option key={tool} value={tool} />
        ))}
      </datalist>
      {mcpToolsLoading[connector.system] && (
        <span className={styles.fieldHint}>Loading MCP tool catalog...</span>
      )}
      {mcpToolsError[connector.system] && (
        <span className={styles.fieldHint}>
          Unable to load MCP tools. You can still enter tool names manually.
        </span>
      )}
      {!mcpServerUrl && (
        <span className={styles.fieldHint}>
          Provide an MCP server URL before enabling MCP for this connector.
        </span>
      )}

      <div className={styles.mcpToolActions}>
        <button
          className={styles.mcpSaveButton}
          onClick={handleSave}
          disabled={!canManage || saving}
        >
          {saving ? 'Saving...' : 'Save Tool Mapping'}
        </button>
      </div>
    </div>
  );
}
