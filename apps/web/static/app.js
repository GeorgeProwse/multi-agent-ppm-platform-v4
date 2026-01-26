const authStatus = document.getElementById("auth-status");
const statusOutput = document.getElementById("status-output");
const workflowOutput = document.getElementById("workflow-output");

const tenantInput = document.getElementById("tenant");
const tokenInput = document.getElementById("token");

const loadConfig = async () => {
  const response = await fetch("/config");
  return response.json();
};

const getHeaders = () => {
  const token = tokenInput.value.trim();
  const tenant = tenantInput.value.trim();
  return {
    Authorization: `Bearer ${token}`,
    "X-Tenant-ID": tenant,
    "Content-Type": "application/json",
  };
};

const setStatus = (element, message, ok = true) => {
  element.textContent = message;
  element.className = ok ? "status ok" : "status error";
};

const validateToken = async () => {
  const config = await loadConfig();
  const response = await fetch(`${config.identity_access_url}/auth/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: tokenInput.value.trim() }),
  });
  const payload = await response.json();
  if (payload.active) {
    setStatus(authStatus, "Token validated. Tenant context locked.");
  } else {
    setStatus(authStatus, "Token invalid or expired.", false);
  }
};

const loadStatus = async () => {
  const config = await loadConfig();
  const response = await fetch(`${config.api_gateway_url}/api/v1/status`, {
    headers: getHeaders(),
  });
  const payload = await response.json();
  statusOutput.textContent = JSON.stringify(payload, null, 2);
};

const startWorkflow = async () => {
  const config = await loadConfig();
  const response = await fetch(`${config.workflow_engine_url}/workflows/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      workflow_id: document.getElementById("workflow-id").value,
      tenant_id: tenantInput.value.trim(),
      classification: "internal",
      payload: { request: "run" },
      actor: { id: "ui-user", type: "user", roles: ["portfolio_admin"] },
    }),
  });
  const payload = await response.json();
  workflowOutput.textContent = JSON.stringify(payload, null, 2);
};

document.getElementById("validate").addEventListener("click", validateToken);
document.getElementById("load-status").addEventListener("click", loadStatus);
document.getElementById("start-workflow").addEventListener("click", startWorkflow);
