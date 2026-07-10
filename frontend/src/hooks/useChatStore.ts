import { useState, useCallback, useRef } from "react";
import type { SSEEvent, SSEEventData, AgentStartEvent } from "../types";

export interface ChatState {
  sessionId: string;
  project: string;
  events: SSEEvent[];
  currentAgent: string | null;
  isConnected: boolean;
  isReconnecting: boolean;
  error: Error | null;
}

const initialState = (sessionId: string, project: string): ChatState => ({
  sessionId,
  project,
  events: [],
  currentAgent: null,
  isConnected: false,
  isReconnecting: false,
  error: null,
});

export function useChatStore(sessionId: string, project: string) {
  const [state, setState] = useState<ChatState>(() => initialState(sessionId, project));
  const eventsRef = useRef<SSEEvent[]>([]);

  const handleEvent = useCallback((event: SSEEvent) => {
    eventsRef.current = [...eventsRef.current, event];

    setState((prev) => {
      const update: Partial<ChatState> = {
        events: eventsRef.current,
      };

      if (event.type === "agent_start") {
        update.currentAgent = (event.data as AgentStartEvent).agent;
      }

      return { ...prev, ...update };
    });
  }, []);

  const setConnected = useCallback((connected: boolean) => {
    setState((prev) => ({ ...prev, isConnected: connected }));
  }, []);

  const setReconnecting = useCallback((reconnecting: boolean) => {
    setState((prev) => ({ ...prev, isReconnecting: reconnecting }));
  }, []);

  const setError = useCallback((error: Error | null) => {
    setState((prev) => ({ ...prev, error }));
  }, []);

  const reset = useCallback(() => {
    eventsRef.current = [];
    setState(initialState(sessionId, project));
  }, [sessionId, project]);

  const agentEvents = state.events.filter(
    (e): e is SSEEvent & { data: AgentStartEvent } => e.type === "agent_start"
  );

  return {
    state,
    agentEvents,
    handleEvent,
    setConnected,
    setReconnecting,
    setError,
    reset,
  };
}
