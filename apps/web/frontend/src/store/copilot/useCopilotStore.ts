import { create } from 'zustand';

export interface AgentExecutionState {
  agentId: string;
  catalogId: string;
  status: 'pending' | 'thinking' | 'completed' | 'error';
  startedAt: number | null;
  completedAt: number | null;
  confidence: number | null;
  intermediateOutput: string | null;
}

export interface ExecutionEvent {
  event_type: string;
  task_id: string;
  agent_id: string;
  catalog_id: string;
  correlation_id: string;
  timestamp: number;
  data: Record<string, unknown>;
  confidence_score: number | null;
}

interface CopilotState {
  activeAgents: Record<string, AgentExecutionState>;
  orchestrationStatus: 'idle' | 'running' | 'completed';
  correlationId: string | null;
  events: ExecutionEvent[];
  startOrchestration: (correlationId: string) => void;
  onAgentEvent: (event: ExecutionEvent) => void;
  reset: () => void;
}

export const useCopilotStore = create<CopilotState>((set) => ({
  activeAgents: {},
  orchestrationStatus: 'idle',
  correlationId: null,
  events: [],

  startOrchestration: (correlationId: string) =>
    set({
      correlationId,
      orchestrationStatus: 'running',
      activeAgents: {},
      events: [],
    }),

  onAgentEvent: (event: ExecutionEvent) =>
    set((state) => {
      const events = [...state.events, event];
      const activeAgents = { ...state.activeAgents };

      switch (event.event_type) {
        case 'agent_started':
          activeAgents[event.task_id] = {
            agentId: event.agent_id,
            catalogId: event.catalog_id,
            status: 'thinking',
            startedAt: event.timestamp,
            completedAt: null,
            confidence: null,
            intermediateOutput: null,
          };
          break;
        case 'agent_completed':
          if (activeAgents[event.task_id]) {
            activeAgents[event.task_id] = {
              ...activeAgents[event.task_id],
              status: 'completed',
              completedAt: event.timestamp,
              confidence: event.confidence_score,
            };
          }
          break;
        case 'agent_error':
          if (activeAgents[event.task_id]) {
            activeAgents[event.task_id] = {
              ...activeAgents[event.task_id],
              status: 'error',
              completedAt: event.timestamp,
            };
          }
          break;
        case 'agent_intermediate':
          if (activeAgents[event.task_id]) {
            activeAgents[event.task_id] = {
              ...activeAgents[event.task_id],
              intermediateOutput: String(event.data?.output ?? ''),
            };
          }
          break;
        case 'orchestration_completed':
          return { events, activeAgents, orchestrationStatus: 'completed' as const };
      }

      return { events, activeAgents };
    }),

  reset: () =>
    set({
      activeAgents: {},
      orchestrationStatus: 'idle',
      correlationId: null,
      events: [],
    }),
}));
