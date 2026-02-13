import { create } from 'zustand';

export interface WorkflowStatusEvent {
  runId: string;
  workflowId: string;
  status: string;
  stepId?: string;
  timestamp: string;
}

export interface ApprovalUpdateEvent {
  approvalId: string;
  runId: string;
  status: string;
  actor?: string;
  timestamp: string;
}

export interface NotificationEvent {
  id: string;
  title: string;
  message: string;
  severity: 'success' | 'failed' | 'info';
  source?: string;
  timestamp: string;
}

type RealtimeEvent =
  | { type: 'workflow_status'; payload: WorkflowStatusEvent }
  | { type: 'approval_update'; payload: ApprovalUpdateEvent }
  | { type: 'notification'; payload: NotificationEvent };

interface RealtimeState {
  connected: boolean;
  workflowUpdates: WorkflowStatusEvent[];
  approvalUpdates: ApprovalUpdateEvent[];
  notifications: NotificationEvent[];
  setConnected: (connected: boolean) => void;
  applyEvent: (event: RealtimeEvent) => void;
}

const cap = <T,>(arr: T[], max = 100) => arr.slice(0, max);

export const useRealtimeStore = create<RealtimeState>((set) => ({
  connected: false,
  workflowUpdates: [],
  approvalUpdates: [],
  notifications: [],
  setConnected: (connected) => set({ connected }),
  applyEvent: (event) => {
    switch (event.type) {
      case 'workflow_status':
        set((state) => ({
          workflowUpdates: cap([event.payload, ...state.workflowUpdates]),
        }));
        break;
      case 'approval_update':
        set((state) => ({
          approvalUpdates: cap([event.payload, ...state.approvalUpdates]),
        }));
        break;
      case 'notification':
        set((state) => ({
          notifications: cap([event.payload, ...state.notifications]),
        }));
        break;
      default:
        break;
    }
  },
}));
