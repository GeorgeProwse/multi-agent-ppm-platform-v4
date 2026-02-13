import { useEffect } from 'react';
import { useAppStore } from '@/store';
import { useRealtimeStore } from '@/store/realtime/useRealtimeStore';

const resolveRealtimeUrl = () => {
  const configured = import.meta.env?.VITE_REALTIME_WS_URL as string | undefined;
  const base = configured ?? 'ws://localhost:8000';
  return `${base.replace(/\/$/, '')}/ws/events`;
};

export function useRealtimeConsole() {
  const { session, tenantContext } = useAppStore();
  const setConnected = useRealtimeStore((state) => state.setConnected);
  const applyEvent = useRealtimeStore((state) => state.applyEvent);

  useEffect(() => {
    if (!session.authenticated || !tenantContext.tenantId) {
      setConnected(false);
      return;
    }

    const params = new URLSearchParams({
      tenant_id: tenantContext.tenantId,
      user_id: session.user?.id ?? 'unknown',
    });

    const ws = new WebSocket(`${resolveRealtimeUrl()}?${params.toString()}`);

    ws.onopen = () => {
      setConnected(true);
      ws.send(
        JSON.stringify({
          type: 'subscribe',
          channels: ['workflow_status', 'approval_update', 'notification'],
        })
      );
    };

    ws.onclose = () => {
      setConnected(false);
    };

    ws.onerror = () => {
      setConnected(false);
    };

    ws.onmessage = (message) => {
      try {
        applyEvent(JSON.parse(message.data as string));
      } catch {
        // Ignore malformed realtime payloads.
      }
    };

    return () => {
      ws.close();
      setConnected(false);
    };
  }, [applyEvent, session.authenticated, session.user?.id, setConnected, tenantContext.tenantId]);
}
