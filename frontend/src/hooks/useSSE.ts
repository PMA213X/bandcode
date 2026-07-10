// 导入 React Hooks：状态管理、副作用处理、性能优化、DOM 引用
import { useState, useEffect, useCallback, useRef } from "react";
// 导入 SSE 相关的类型定义
import type { SSEEvent, SSEEventType, SSEEventData } from "../types";

/**
 * SSE Hook 配置选项接口
 */
interface UseSSEOptions {
  sessionId: string;     // 会话 ID
  project: string;       // 项目名称
  message: string;       // 用户消息内容
  maxRetries?: number;   // 最大重试次数，默认 3 次
  onEvent?: (event: SSEEvent) => void;      // 每收到一个事件时的回调
  onComplete?: (data: SSEEventData) => void; // 收到完成事件时的回调
  onError?: (error: Error) => void;          // 发生错误时的回调
}

/**
 * SSE Hook 返回值接口
 */
interface UseSSEReturn {
  events: SSEEvent[];        // 所有收到的事件列表
  isConnected: boolean;      // 是否已连接
  isReconnecting: boolean;   // 是否正在重连
  retryCount: number;        // 当前重试次数
  error: Error | null;       // 错误信息
  disconnect: () => void;    // 手动断开连接
  clearEvents: () => void;   // 清空事件列表
}

/**
 * 支持的 SSE 事件类型列表
 * 与后端 SSEEventType 定义保持一致
 */
const SSE_EVENT_TYPES: SSEEventType[] = [
  "agent_start",        // Agent 开始执行
  "constraint_result",  // 约束检索结果
  "plan",               // Planner 输出计划
  "approval_required",  // 需要用户审批
  "tool_call",          // Tool 调用
  "code",               // 代码生成
  "test_result",        // 测试结果
  "review_result",      // 审查结果
  "memory_update",      // Memory 更新
  "done",               // 任务完成
  "error",              // 错误
];

/**
 * SSE (Server-Sent Events) 连接管理 Hook
 * 封装与后端 /api/chat/stream 的 SSE 通信
 * 支持自动重连、事件解析、状态管理
 *
 * @param options - 配置选项
 * @returns SSE 连接状态和控制方法
 */
export function useSSE(options: UseSSEOptions): UseSSEReturn {
  // 解构配置，设置默认最大重试次数为 3
  const { maxRetries = 3 } = options;

  // 状态定义
  const [events, setEvents] = useState<SSEEvent[]>([]);           // 事件列表
  const [isConnected, setIsConnected] = useState(false);           // 连接状态
  const [isReconnecting, setIsReconnecting] = useState(false);     // 重连状态
  const [retryCount, setRetryCount] = useState(0);                 // 重试计数
  const [error, setError] = useState<Error | null>(null);          // 错误信息
  const eventSourceRef = useRef<EventSource | null>(null);         // EventSource 引用
  const doneRef = useRef(false);                                   // 是否已完成标记

  /**
   * 建立 SSE 连接
   * 使用 useCallback 优化，仅在参数变化时重新创建
   */
  const connect = useCallback(() => {
    // 构建查询参数
    const params = new URLSearchParams({
      session_id: options.sessionId,
      project: options.project,
      message: options.message,
    });

    // 创建 EventSource 连接到后端 SSE 端点
    const eventSource = new EventSource(`/api/chat/stream?${params.toString()}`);
    doneRef.current = false;  // 重置完成标记

    // 连接成功回调
    eventSource.onopen = () => {
      setIsConnected(true);        // 标记已连接
      setIsReconnecting(false);    // 停止重连状态
      setError(null);              // 清除错误
      setRetryCount(0);            // 重置重试计数
    };

    // 为每种事件类型注册监听器
    SSE_EVENT_TYPES.forEach((type) => {
      eventSource.addEventListener(type, (e: MessageEvent) => {
        try {
          // 解析事件数据
          const data = JSON.parse(e.data);
          const event: SSEEvent = { type, data };

          // 添加到事件列表
          setEvents((prev) => [...prev, event]);
          // 触发回调
          options.onEvent?.(event);

          // 如果是完成事件，关闭连接
          if (type === "done") {
            doneRef.current = true;
            options.onComplete?.(data);
            eventSource.close();
            setIsConnected(false);
          }
        } catch {
          // 解析失败，设置错误
          setError(new Error(`SSE事件解析失败: ${type}`));
        }
      });
    });

    // 连接错误回调
    eventSource.onerror = () => {
      eventSource.close();        // 关闭连接
      setIsConnected(false);      // 标记断开

      // 如果已完成，不再重连
      if (doneRef.current) return;

      // 重试逻辑
      setRetryCount((prev) => {
        const next = prev + 1;
        if (next <= maxRetries) {
          // 还有重试次数，执行指数退避重连
          setIsReconnecting(true);
          const delay = Math.min(1000 * 2 ** (next - 1), 10000);  // 指数退避，最大 10 秒
          setTimeout(() => connect(), delay);
        } else {
          // 超过最大重试次数，报告错误
          const err = new Error(`SSE连接失败，已重试${maxRetries}次`);
          setError(err);
          setIsReconnecting(false);
          options.onError?.(err);
        }
        return next;
      });
    };

    // 保存 EventSource 引用
    eventSourceRef.current = eventSource;

    // 返回清理函数
    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [options.sessionId, options.project, options.message, maxRetries]);

  // 组件挂载时建立连接，卸载时清理
  useEffect(() => {
    const cleanup = connect();
    return cleanup;
  }, [connect]);

  /**
   * 手动断开连接
   */
  const disconnect = useCallback(() => {
    doneRef.current = true;
    eventSourceRef.current?.close();
    setIsConnected(false);
    setIsReconnecting(false);
  }, []);

  /**
   * 清空事件列表
   */
  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  // 返回状态和控制方法
  return { events, isConnected, isReconnecting, retryCount, error, disconnect, clearEvents };
}
