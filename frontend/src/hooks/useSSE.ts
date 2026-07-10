import { useState, useEffect, useCallback, useRef } from "react";
import type { SSEEvent, SSEEventType, SSEEventData } from "../types";

interface UseSSEOptions {
  sessionId: string;
  project: string;
  message: string;
  onEvent?: (event: SSEEvent) => void;
  onComplete?: (data: SSEEventData) => void;
  onError?: (error: Error) => void;
}

interface UseSSEReturn {
  events: SSEEvent[];
  isConnected: boolean;
  error: Error | null;
  disconnect: () => void;
  clearEvents: () => void;
}

const SSE_EVENT_TYPES: SSEEventType[] = [
  "agent_start",
  "constraint_result",
  "plan",
  "approval_required",
  "tool_call",
  "code",
  "test_result",
  "review_result",
  "memory_update",
  "done",
  "error",
];

export function useSSE(options: UseSSEOptions): UseSSEReturn {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    const params = new URLSearchParams({
      session_id: options.sessionId,
      project: options.project,
      message: options.message,
    });

    const eventSource = new EventSource(`/api/chat/stream?${params.toString()}`);

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    SSE_EVENT_TYPES.forEach((type) => {
      eventSource.addEventListener(type, (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          const event: SSEEvent = { type, data };
          setEvents((prev) => [...prev, event]);
          options.onEvent?.(event);

          if (type === "done") {
            options.onComplete?.(data);
            eventSource.close();
            setIsConnected(false);
          }
        } catch {
          setError(new Error(`Failed to parse SSE event: ${type}`));
        }
      });
    });

    eventSource.onerror = () => {
      const err = new Error("SSE connection error");
      setError(err);
      setIsConnected(false);
      options.onError?.(err);
      eventSource.close();
    };

    eventSourceRef.current = eventSource;

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [options.sessionId, options.project, options.message]);

  useEffect(() => {
    const cleanup = connect();
    return cleanup;
  }, [connect]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    setIsConnected(false);
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  return { events, isConnected, error, disconnect, clearEvents };
}
