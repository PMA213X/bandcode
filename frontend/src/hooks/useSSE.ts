import { useState, useEffect, useCallback, useRef } from "react";
import type { SSEEvent, SSEEventType, SSEEventData } from "../types";

interface UseSSEOptions {
  sessionId: string;
  project: string;
  message: string;
  maxRetries?: number;
  onEvent?: (event: SSEEvent) => void;
  onComplete?: (data: SSEEventData) => void;
  onError?: (error: Error) => void;
}

interface UseSSEReturn {
  events: SSEEvent[];
  isConnected: boolean;
  isReconnecting: boolean;
  retryCount: number;
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
  const { maxRetries = 3 } = options;
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [error, setError] = useState<Error | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const doneRef = useRef(false);

  const connect = useCallback(() => {
    const params = new URLSearchParams({
      session_id: options.sessionId,
      project: options.project,
      message: options.message,
    });

    const eventSource = new EventSource(`/api/chat/stream?${params.toString()}`);
    doneRef.current = false;

    eventSource.onopen = () => {
      setIsConnected(true);
      setIsReconnecting(false);
      setError(null);
      setRetryCount(0);
    };

    SSE_EVENT_TYPES.forEach((type) => {
      eventSource.addEventListener(type, (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          const event: SSEEvent = { type, data };
          setEvents((prev) => [...prev, event]);
          options.onEvent?.(event);

          if (type === "done") {
            doneRef.current = true;
            options.onComplete?.(data);
            eventSource.close();
            setIsConnected(false);
          }
        } catch {
          setError(new Error(`SSE事件解析失败: ${type}`));
        }
      });
    });

    eventSource.onerror = () => {
      eventSource.close();
      setIsConnected(false);

      if (doneRef.current) return;

      setRetryCount((prev) => {
        const next = prev + 1;
        if (next <= maxRetries) {
          setIsReconnecting(true);
          const delay = Math.min(1000 * 2 ** (next - 1), 10000);
          setTimeout(() => connect(), delay);
        } else {
          const err = new Error(`SSE连接失败，已重试${maxRetries}次`);
          setError(err);
          setIsReconnecting(false);
          options.onError?.(err);
        }
        return next;
      });
    };

    eventSourceRef.current = eventSource;

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [options.sessionId, options.project, options.message, maxRetries]);

  useEffect(() => {
    const cleanup = connect();
    return cleanup;
  }, [connect]);

  const disconnect = useCallback(() => {
    doneRef.current = true;
    eventSourceRef.current?.close();
    setIsConnected(false);
    setIsReconnecting(false);
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  return { events, isConnected, isReconnecting, retryCount, error, disconnect, clearEvents };
}
