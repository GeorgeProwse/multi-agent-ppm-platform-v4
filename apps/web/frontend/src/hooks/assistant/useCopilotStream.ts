import { useEffect, useRef } from 'react';
import { useCopilotStore } from '@/store/copilot';

export function useCopilotStream(correlationId: string | null) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const { onAgentEvent, startOrchestration } = useCopilotStore();

  useEffect(() => {
    if (!correlationId) return;

    startOrchestration(correlationId);
    const es = new EventSource(`/api/copilot/stream/${correlationId}`);
    eventSourceRef.current = es;

    const handleEvent = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data);
        onAgentEvent(data);
      } catch {
        // ignore malformed events
      }
    };

    es.addEventListener('agent_started', handleEvent);
    es.addEventListener('agent_thinking', handleEvent);
    es.addEventListener('agent_intermediate', handleEvent);
    es.addEventListener('agent_completed', handleEvent);
    es.addEventListener('agent_error', handleEvent);
    es.addEventListener('orchestration_started', handleEvent);
    es.addEventListener('orchestration_completed', (e) => {
      handleEvent(e);
      es.close();
    });
    es.addEventListener('error', handleEvent);

    es.onerror = () => {
      es.close();
    };

    return () => {
      es.close();
      eventSourceRef.current = null;
    };
  }, [correlationId, onAgentEvent, startOrchestration]);
}
