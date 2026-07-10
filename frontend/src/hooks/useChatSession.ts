import { useState, useCallback } from "react";
import { api } from "../services/api";
import { useSSE } from "../hooks/useSSE";
import { useChatStore } from "../hooks/useChatStore";
import type { SSEEvent, ApprovalRequiredEvent } from "../types";

interface UseChatSessionOptions {
  sessionId: string;
  project: string;
  maxRetries?: number;
}

export function useChatSession({ sessionId, project, maxRetries = 3 }: UseChatSessionOptions) {
  const [pendingApproval, setPendingApproval] = useState<ApprovalRequiredEvent | null>(null);

  const {
    state,
    agentEvents,
    handleEvent,
    setConnected,
    setReconnecting,
    setError,
    reset,
  } = useChatStore(sessionId, project);

  const sendMessage = useCallback(
    (message: string) => {
      reset();
      setPendingApproval(null);

      const sse = useSSE({
        sessionId,
        project,
        message,
        maxRetries,
        onEvent: handleEvent,
        onComplete: () => setConnected(false),
        onError: (err) => setError(err),
      });

      return sse;
    },
    [sessionId, project, maxRetries]
  );

  const approveAction = useCallback(async () => {
    if (!pendingApproval) return;
    setPendingApproval(null);
  }, [pendingApproval]);

  const rejectAction = useCallback(async () => {
    if (!pendingApproval) return;
    setPendingApproval(null);
  }, [pendingApproval]);

  return {
    state,
    agentEvents,
    pendingApproval,
    sendMessage,
    approveAction,
    rejectAction,
    reset,
  };
}
