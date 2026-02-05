export interface AssistantResponsePayload {
  summary?: string | null;
  items?: string[] | null;
  response?: string | null;
}

export function formatAssistantResponse(payload: AssistantResponsePayload): string {
  if (typeof payload === 'string') {
    return payload;
  }
  const summary = payload.summary ?? payload.response ?? '';
  const items = payload.items ?? [];
  if (!items.length) {
    return summary;
  }
  const list = items.map((item) => `• ${item}`).join('\n');
  if (!summary) {
    return list;
  }
  return `${summary}\n${list}`;
}
