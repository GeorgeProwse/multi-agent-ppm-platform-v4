/**
 * ConnectorConfigModal - Modal for configuring a connector's connection settings,
 * MCP options, sync direction/frequency, and testing the connection.
 */

import { useEffect, useMemo, useState } from 'react';
import { useConnectorStore, type ConnectorType } from '@/store/connectors';
import { Icon } from '@/components/icon/Icon';
import {
  buildInitialToolMap,
  type ConnectorConfigModalProps,
} from './connectorGalleryTypes';
import { ConnectorIcon } from './ConnectorIcon';
import styles from './ConnectorGallery.module.css';

export function ConnectorConfigModal({
  connector,
  onClose,
  onSave,
  onTestConnection,
  testingConnection,
  testResult,
  clearTestResult,
}: ConnectorConfigModalProps) {
  const customFields = connector.custom_fields ?? {};
  const isIoT = connector.category === 'iot';
  const isSlack = connector.connector_id === 'slack';
  const isWorkday = connector.connector_id === 'workday';
  const mcpFeatureEnabled = connector.mcp_feature_enabled ?? true;
  const { mcpToolsBySystem, mcpToolsLoading, mcpToolsError, fetchMcpTools } = useConnectorStore();
  const [connectorType, setConnectorType] = useState<ConnectorType>(
    connector.mcp_feature_enabled === false ? 'rest' : connector.connector_type ?? 'rest'
  );
  const [mcpServerId, setMcpServerId] = useState(connector.mcp_server_id ?? '');
  const [mcpServerUrl, setMcpServerUrl] = useState(connector.mcp_server_url ?? '');
  const [mcpScopes, setMcpScopes] = useState<string[]>(connector.mcp_scopes ?? []);
  const [mcpToolMap, setMcpToolMap] = useState<Record<string, string>>(() =>
    buildInitialToolMap(connector)
  );
  const [instanceUrl, setInstanceUrl] = useState(connector.instance_url || '');
  const [projectKey, setProjectKey] = useState(connector.project_key || '');
  const [deviceEndpoint, setDeviceEndpoint] = useState(
    (customFields.device_endpoint as string) || connector.instance_url || ''
  );
  const [authToken, setAuthToken] = useState((customFields.auth_token as string) || '');
  const [sensorTypes, setSensorTypes] = useState((customFields.sensor_types as string) || '');
  const [slackBotToken, setSlackBotToken] = useState((customFields.slack_bot_token as string) || '');
  const [slackSigningSecret, setSlackSigningSecret] = useState(
    (customFields.slack_signing_secret as string) || ''
  );
  const [slackDefaultChannel, setSlackDefaultChannel] = useState(
    (customFields.default_channel as string) || ''
  );
  const [workdayTenant, setWorkdayTenant] = useState((customFields.tenant as string) || '');
  const [workdayClientId, setWorkdayClientId] = useState((customFields.client_id as string) || '');
  const [workdayClientSecret, setWorkdayClientSecret] = useState(
    (customFields.client_secret as string) || ''
  );
  const [workdayRefreshToken, setWorkdayRefreshToken] = useState(
    (customFields.refresh_token as string) || ''
  );
  const [workdayTokenUrl, setWorkdayTokenUrl] = useState((customFields.token_url as string) || '');
  const [syncDirection, setSyncDirection] = useState(connector.sync_direction);
  const [syncFrequency, setSyncFrequency] = useState(connector.sync_frequency);
  const [saving, setSaving] = useState(false);
  const connectionTarget =
    connectorType === 'mcp' ? mcpServerUrl : isIoT ? deviceEndpoint : instanceUrl;
  const mcpServerOptions = [
    { id: 'mcp-core', label: 'Core MCP Server' },
    { id: 'mcp-analytics', label: 'Analytics MCP Server' },
    { id: 'mcp-integrations', label: 'Integrations MCP Server' },
  ];
  const toolOptions = useMemo(() => {
    const preferred = connector.supported_operations.length
      ? connector.supported_operations
      : Object.keys(mcpToolMap);
    const fallback = preferred.length ? preferred : ['projects.read', 'projects.write', 'resources.read'];
    const extras = Object.keys(mcpToolMap).filter((operation) => !fallback.includes(operation));
    return [...fallback, ...extras];
  }, [connector.supported_operations, mcpToolMap]);
  const toolCatalog = mcpToolsBySystem[connector.system] ?? [];
  const toolCatalogNames = toolCatalog.map((tool) => tool.name);
  const scopeOptions = ['projects:read', 'projects:write', 'resources:read', 'portfolio:read'];
  const selectedTools = useMemo(
    () =>
      Array.from(
        new Set(
          Object.values(mcpToolMap)
            .map((tool) => tool.trim())
            .filter(Boolean)
        )
      ),
    [mcpToolMap]
  );

  useEffect(() => {
    setConnectorType(
      connector.mcp_feature_enabled === false ? 'rest' : connector.connector_type ?? 'rest'
    );
    setMcpServerId(connector.mcp_server_id ?? '');
    setMcpServerUrl(connector.mcp_server_url ?? '');
    setMcpScopes(connector.mcp_scopes ?? []);
    setMcpToolMap(buildInitialToolMap(connector));
  }, [connector]);

  useEffect(() => {
    if (connectorType === 'mcp' && mcpFeatureEnabled) {
      fetchMcpTools(connector.system);
    }
  }, [connector.system, connectorType, fetchMcpTools, mcpFeatureEnabled]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const effectiveInstanceUrl = isIoT ? deviceEndpoint : instanceUrl;
      const customPayload: Record<string, unknown> = {};
      if (isIoT) {
        customPayload.device_endpoint = deviceEndpoint;
        customPayload.auth_token = authToken;
        customPayload.sensor_types = sensorTypes;
      }
      if (isSlack) {
        customPayload.slack_bot_token = slackBotToken;
        customPayload.slack_signing_secret = slackSigningSecret;
        customPayload.default_channel = slackDefaultChannel;
      }
      if (isWorkday) {
        customPayload.tenant = workdayTenant;
        customPayload.client_id = workdayClientId;
        customPayload.client_secret = workdayClientSecret;
        customPayload.refresh_token = workdayRefreshToken;
        customPayload.token_url = workdayTokenUrl;
      }
      const normalizedToolMap = Object.entries(mcpToolMap).reduce<Record<string, string>>(
        (acc, [operation, tool]) => {
          const trimmed = tool.trim();
          if (trimmed) {
            acc[operation] = trimmed;
          }
          return acc;
        },
        {}
      );
      await onSave(connector.connector_id, {
        instance_url: effectiveInstanceUrl,
        project_key: projectKey,
        connector_type: connectorType,
        mcp_server_id: connectorType === 'mcp' ? mcpServerId : undefined,
        mcp_server_url: connectorType === 'mcp' ? mcpServerUrl : undefined,
        mcp_tool_map:
          connectorType === 'mcp' && Object.keys(normalizedToolMap).length
            ? normalizedToolMap
            : undefined,
        mcp_scopes: connectorType === 'mcp' && mcpScopes.length ? mcpScopes : undefined,
        sync_direction: syncDirection,
        sync_frequency: syncFrequency,
        custom_fields: Object.keys(customPayload).length ? customPayload : undefined,
      });
      onClose();
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    clearTestResult();
    const effectiveInstanceUrl =
      connectorType === 'mcp' ? mcpServerUrl : isIoT ? deviceEndpoint : instanceUrl;
    await onTestConnection(connector.connector_id, effectiveInstanceUrl, projectKey);
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <div className={styles.modalTitleSection}>
            <ConnectorIcon name={connector.icon} />
            <h2 className={styles.modalTitle}>{connector.name} Configuration</h2>
          </div>
          <button
            className={styles.modalClose}
            onClick={onClose}
            aria-label="Close connector configuration"
          >
            <Icon semantic="actions.cancelDismiss" label="Close connector configuration" />
          </button>
        </div>

        <div className={styles.modalBody}>
          <p className={styles.modalDescription}>{connector.description}</p>

          <div className={styles.configSection}>
            <h3 className={styles.sectionTitle}>Connection Settings</h3>

            <div className={styles.formField}>
              <label className={styles.fieldLabel}>MCP Enabled</label>
              <label className={styles.mcpToggle}>
                <span>{connectorType === 'mcp' ? 'MCP enabled' : 'Use REST'}</span>
                <span className={styles.mcpToggleSwitch}>
                  <input
                    type="checkbox"
                    checked={connectorType === 'mcp'}
                    onChange={(event) =>
                      setConnectorType(event.target.checked ? 'mcp' : 'rest')
                    }
                    disabled={!mcpFeatureEnabled}
                    aria-label={`Enable MCP for ${connector.name}`}
                  />
                  <span className={styles.toggleSlider}></span>
                </span>
              </label>
              <span className={styles.fieldHint}>
                Enable MCP to run this connector via the managed runtime instead of REST.
              </span>
              {!mcpFeatureEnabled && (
                <span className={styles.fieldHint}>
                  MCP is disabled by feature flag for this system.
                </span>
              )}
            </div>

            {connectorType === 'mcp' && (
              <>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>MCP Server</label>
                  <select
                    className={styles.fieldSelect}
                    value={mcpServerId}
                    onChange={(e) => setMcpServerId(e.target.value)}
                  >
                    <option value="">Select a server</option>
                    {mcpServerOptions.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.label}
                      </option>
                    ))}
                    {connector.mcp_server_id && !mcpServerOptions.some((option) => option.id === connector.mcp_server_id) && (
                      <option value={connector.mcp_server_id}>Current: {connector.mcp_server_id}</option>
                    )}
                  </select>
                  <span className={styles.fieldHint}>
                    Target MCP server for this connector.
                  </span>
                </div>

                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>MCP Server URL</label>
                  <input
                    type="url"
                    className={styles.fieldInput}
                    placeholder="https://mcp.example.com"
                    value={mcpServerUrl}
                    onChange={(e) => setMcpServerUrl(e.target.value)}
                  />
                  <span className={styles.fieldHint}>
                    Override the MCP endpoint when using a custom server.
                  </span>
                </div>

                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>MCP Tool Map</label>
                  <div className={styles.mcpToolMap}>
                    {toolOptions.map((operation) => (
                      <div key={operation} className={styles.mcpToolRow}>
                        <label className={styles.mcpToolLabel} htmlFor={`${connector.connector_id}-${operation}`}>
                          {operation}
                        </label>
                        <input
                          id={`${connector.connector_id}-${operation}`}
                          className={styles.mcpToolInput}
                          type="text"
                          value={mcpToolMap[operation] ?? ''}
                          onChange={(event) =>
                            setMcpToolMap((prev) => ({
                              ...prev,
                              [operation]: event.target.value,
                            }))
                          }
                          placeholder="e.g., portfolio.read"
                          list={`${connector.connector_id}-mcp-tools`}
                        />
                      </div>
                    ))}
                  </div>
                  <datalist id={`${connector.connector_id}-mcp-tools`}>
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
                  <span className={styles.fieldHint}>
                    Map connector operations to MCP tools. Tool suggestions come from the MCP server.
                  </span>
                </div>

                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>MCP Scopes</label>
                  <select
                    className={styles.fieldSelect}
                    multiple
                    value={mcpScopes}
                    onChange={(e) =>
                      setMcpScopes(Array.from(e.target.selectedOptions, (option) => option.value))
                    }
                  >
                    {scopeOptions.map((scope) => (
                      <option key={scope} value={scope}>
                        {scope}
                      </option>
                    ))}
                  </select>
                  <span className={styles.fieldHint}>
                    Select scopes that the MCP runtime can access.
                  </span>
                </div>
              </>
            )}

            <div className={styles.formField}>
              <label className={styles.fieldLabel}>
                {isIoT ? 'Device Endpoint' : 'Instance URL'}
              </label>
              <input
                type="url"
                className={styles.fieldInput}
                placeholder={isIoT ? 'https://device-gateway.example.com' : 'https://your-instance.example.com'}
                value={isIoT ? deviceEndpoint : instanceUrl}
                onChange={(e) =>
                  isIoT ? setDeviceEndpoint(e.target.value) : setInstanceUrl(e.target.value)
                }
              />
              <span className={styles.fieldHint}>
                {isIoT
                  ? 'The REST endpoint for your device gateway or IoT hub'
                  : `The base URL of your ${connector.name} instance`}
              </span>
            </div>

            {isIoT && (
              <>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Authentication Token</label>
                  <input
                    type="password"
                    className={styles.fieldInput}
                    placeholder="e.g., bearer token"
                    value={authToken}
                    onChange={(e) => setAuthToken(e.target.value)}
                  />
                  <span className={styles.fieldHint}>
                    Token or API key used to authenticate with the IoT device gateway
                  </span>
                </div>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Supported Sensor Types</label>
                  <input
                    type="text"
                    className={styles.fieldInput}
                    placeholder="temperature, humidity, vibration"
                    value={sensorTypes}
                    onChange={(e) => setSensorTypes(e.target.value)}
                  />
                  <span className={styles.fieldHint}>
                    Comma-separated sensor types for ingestion routing
                  </span>
                </div>
              </>
            )}

            {isSlack && (
              <>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Slack Bot Token</label>
                  <input
                    type="password"
                    className={styles.fieldInput}
                    placeholder="xoxb-..."
                    value={slackBotToken}
                    onChange={(e) => setSlackBotToken(e.target.value)}
                  />
                  <span className={styles.fieldHint}>
                    Used to authenticate API requests and send outbound messages.
                  </span>
                </div>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Signing Secret</label>
                  <input
                    type="password"
                    className={styles.fieldInput}
                    placeholder="Signing secret"
                    value={slackSigningSecret}
                    onChange={(e) => setSlackSigningSecret(e.target.value)}
                  />
                  <span className={styles.fieldHint}>
                    Required to validate Slack events and webhook signatures.
                  </span>
                </div>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Default Channel</label>
                  <input
                    type="text"
                    className={styles.fieldInput}
                    placeholder="e.g., #project-updates"
                    value={slackDefaultChannel}
                    onChange={(e) => setSlackDefaultChannel(e.target.value)}
                  />
                  <span className={styles.fieldHint}>
                    Optional channel used when no target is provided by the sync job.
                  </span>
                </div>
              </>
            )}

            {isWorkday && (
              <>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Tenant</label>
                  <input
                    type="text"
                    className={styles.fieldInput}
                    placeholder="e.g., acme"
                    value={workdayTenant}
                    onChange={(e) => setWorkdayTenant(e.target.value)}
                  />
                  <span className={styles.fieldHint}>
                    Workday tenant identifier used for API routing.
                  </span>
                </div>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Client ID</label>
                  <input
                    type="text"
                    className={styles.fieldInput}
                    placeholder="Client ID"
                    value={workdayClientId}
                    onChange={(e) => setWorkdayClientId(e.target.value)}
                  />
                  <span className={styles.fieldHint}>OAuth2 client identifier.</span>
                </div>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Client Secret</label>
                  <input
                    type="password"
                    className={styles.fieldInput}
                    placeholder="Client secret"
                    value={workdayClientSecret}
                    onChange={(e) => setWorkdayClientSecret(e.target.value)}
                  />
                  <span className={styles.fieldHint}>OAuth2 client secret used to fetch tokens.</span>
                </div>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Refresh Token</label>
                  <input
                    type="password"
                    className={styles.fieldInput}
                    placeholder="Refresh token"
                    value={workdayRefreshToken}
                    onChange={(e) => setWorkdayRefreshToken(e.target.value)}
                  />
                  <span className={styles.fieldHint}>Used to refresh access tokens for Workday.</span>
                </div>
                <div className={styles.formField}>
                  <label className={styles.fieldLabel}>Token URL (Optional)</label>
                  <input
                    type="url"
                    className={styles.fieldInput}
                    placeholder="https://wd3-impl-services1.workday.com/ccx/oauth2/token"
                    value={workdayTokenUrl}
                    onChange={(e) => setWorkdayTokenUrl(e.target.value)}
                  />
                  <span className={styles.fieldHint}>
                    Override the default token URL when using a custom Workday environment.
                  </span>
                </div>
              </>
            )}

            {connector.connector_id === 'jira' && (
              <div className={styles.formField}>
                <label className={styles.fieldLabel}>Project Key (Optional)</label>
                <input
                  type="text"
                  className={styles.fieldInput}
                  placeholder="e.g., PROJ"
                  value={projectKey}
                  onChange={(e) => setProjectKey(e.target.value)}
                />
                <span className={styles.fieldHint}>
                  Filter issues to a specific project
                </span>
              </div>
            )}

            <div className={styles.envVarNotice}>
              <strong>Note:</strong> API credentials must be configured via environment variables:
              <ul>
                {connector.env_vars.map((envVar) => (
                  <li key={envVar}><code>{envVar}</code></li>
                ))}
              </ul>
            </div>
          </div>

          <div className={styles.configSection}>
            <h3 className={styles.sectionTitle}>Configuration Summary</h3>
            <div className={styles.summaryGrid}>
              <div>
                <span className={styles.summaryLabel}>Transport</span>
                <span className={styles.summaryValue}>{connectorType === 'mcp' ? 'MCP' : 'REST'}</span>
              </div>
              <div>
                <span className={styles.summaryLabel}>MCP Server</span>
                <span className={styles.summaryValue}>
                  {connectorType === 'mcp' ? mcpServerId || 'Not set' : 'REST'}
                </span>
              </div>
              <div>
                <span className={styles.summaryLabel}>MCP Tool</span>
                <span className={styles.summaryValue}>
                  {connectorType === 'mcp'
                    ? selectedTools.length
                      ? selectedTools.join(', ')
                      : 'Not set'
                    : 'REST'}
                </span>
              </div>
              <div>
                <span className={styles.summaryLabel}>MCP Scopes</span>
                <span className={styles.summaryValue}>
                  {connectorType === 'mcp'
                    ? mcpScopes.length
                      ? mcpScopes.join(', ')
                      : 'Not set'
                    : 'REST'}
                </span>
              </div>
            </div>
          </div>

          <div className={styles.configSection}>
            <h3 className={styles.sectionTitle}>Sync Settings</h3>

            <div className={styles.formField}>
              <label className={styles.fieldLabel}>Sync Direction</label>
              <select
                className={styles.fieldSelect}
                value={syncDirection}
                onChange={(e) => setSyncDirection(e.target.value as typeof syncDirection)}
              >
                {connector.supported_sync_directions.includes('inbound') && (
                  <option value="inbound">Inbound (Read from {connector.name})</option>
                )}
                {connector.supported_sync_directions.includes('outbound') && (
                  <option value="outbound">Outbound (Write to {connector.name})</option>
                )}
                {connector.supported_sync_directions.includes('bidirectional') && (
                  <option value="bidirectional">Bidirectional (Read & Write)</option>
                )}
              </select>
            </div>

            <div className={styles.formField}>
              <label className={styles.fieldLabel}>Sync Frequency</label>
              <select
                className={styles.fieldSelect}
                value={syncFrequency}
                onChange={(e) => setSyncFrequency(e.target.value as typeof syncFrequency)}
              >
                <option value="realtime">Real-time (via webhooks)</option>
                <option value="hourly">Hourly</option>
                <option value="every_4_hours">Every 4 hours</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="manual">Manual only</option>
              </select>
            </div>
          </div>

          {/* Test Connection Section */}
          <div className={styles.testConnectionSection}>
            <button
              className={styles.testButton}
              onClick={handleTestConnection}
              disabled={testingConnection || !connectionTarget}
            >
              {testingConnection ? 'Testing...' : 'Test Connection'}
            </button>

            {testResult && (
              <div className={`${styles.testResult} ${styles[testResult.status as 'connected' | 'failed' | 'unauthorized' | 'timeout' | 'invalid_config']}`}>
                <span className={styles.testResultIcon}>
                  <Icon
                    semantic={testResult.status === 'connected' ? 'status.success' : 'status.error'}
                    decorative
                    size="sm"
                  />
                </span>
                <div className={styles.testResultContent}>
                  <strong>{testResult.status === 'connected' ? 'Connected' : 'Failed'}</strong>
                  <p>{testResult.message}</p>
                  {testResult.details && testResult.status === 'connected' && (
                    <ul className={styles.testDetails}>
                      {typeof testResult.details?.user !== 'undefined' && <li>User: {String(testResult.details.user)}</li>}
                      {typeof testResult.details?.email !== 'undefined' && <li>Email: {String(testResult.details.email)}</li>}
                      {typeof testResult.details?.project !== 'undefined' && <li>Project: {String(testResult.details.project)}</li>}
                    </ul>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className={styles.modalFooter}>
          <button className={styles.cancelButton} onClick={onClose}>
            Cancel
          </button>
          <button
            className={styles.saveButton}
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </div>
    </div>
  );
}
