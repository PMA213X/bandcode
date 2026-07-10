// 导入 React Hooks
import { useState, useCallback, useRef } from "react";
// 导入 SSE 事件类型
import type { SSEEvent, SSEEventData, AgentStartEvent } from "../types";

/**
 * 聊天状态接口
 * 定义聊天会话的所有状态数据
 */
export interface ChatState {
  sessionId: string;        // 会话 ID
  project: string;          // 项目名称
  events: SSEEvent[];       // 所有收到的 SSE 事件列表
  currentAgent: string | null;  // 当前活跃的 Agent 名称
  isConnected: boolean;     // 是否已连接
  isReconnecting: boolean;  // 是否正在重连
  error: Error | null;      // 错误信息
}

/**
 * 创建初始状态
 * @param sessionId - 会话 ID
 * @param project - 项目名称
 * @returns 初始聊天状态对象
 */
const initialState = (sessionId: string, project: string): ChatState => ({
  sessionId,
  project,
  events: [],              // 空事件列表
  currentAgent: null,      // 无活跃 Agent
  isConnected: false,      // 未连接
  isReconnecting: false,   // 未重连
  error: null,             // 无错误
});

/**
 * 聊天状态管理 Hook
 * 集中管理聊天会话的所有状态，提供状态更新方法
 *
 * @param sessionId - 会话 ID
 * @param project - 项目名称
 * @returns 状态和控制方法
 */
export function useChatStore(sessionId: string, project: string) {
  // 状态：使用函数式初始化，避免重复计算
  const [state, setState] = useState<ChatState>(() => initialState(sessionId, project));
  // 事件引用：用于累积事件，避免状态更新的闭包问题
  const eventsRef = useRef<SSEEvent[]>([]);

  /**
   * 处理新收到的 SSE 事件
   * 更新事件列表和当前 Agent 状态
   */
  const handleEvent = useCallback((event: SSEEvent) => {
    // 添加到事件引用
    eventsRef.current = [...eventsRef.current, event];

    // 更新状态
    setState((prev) => {
      const update: Partial<ChatState> = {
        events: eventsRef.current,  // 更新事件列表
      };

      // 如果是 Agent 启动事件，更新当前 Agent
      if (event.type === "agent_start") {
        update.currentAgent = (event.data as AgentStartEvent).agent;
      }

      return { ...prev, ...update };
    });
  }, []);

  /**
   * 设置连接状态
   */
  const setConnected = useCallback((connected: boolean) => {
    setState((prev) => ({ ...prev, isConnected: connected }));
  }, []);

  /**
   * 设置重连状态
   */
  const setReconnecting = useCallback((reconnecting: boolean) => {
    setState((prev) => ({ ...prev, isReconnecting: reconnecting }));
  }, []);

  /**
   * 设置错误信息
   */
  const setError = useCallback((error: Error | null) => {
    setState((prev) => ({ ...prev, error }));
  }, []);

  /**
   * 重置状态到初始值
   */
  const reset = useCallback(() => {
    eventsRef.current = [];
    setState(initialState(sessionId, project));
  }, [sessionId, project]);

  // 提取所有 Agent 启动事件，用于显示 Agent 历史
  const agentEvents = state.events.filter(
    (e): e is SSEEvent & { data: AgentStartEvent } => e.type === "agent_start"
  );

  // 返回状态和控制方法
  return {
    state,          // 当前状态
    agentEvents,    // Agent 启动事件列表
    handleEvent,    // 事件处理函数
    setConnected,   // 设置连接状态
    setReconnecting,// 设置重连状态
    setError,       // 设置错误
    reset,          // 重置状态
  };
}
