// 导入 React Hooks
import { useState, useCallback } from "react";
// 导入 API 客户端
import { api } from "../services/api";
// 导入 SSE Hook
import { useSSE } from "../hooks/useSSE";
// 导入聊天状态管理 Hook
import { useChatStore } from "../hooks/useChatStore";
// 导入类型定义
import type { SSEEvent, ApprovalRequiredEvent } from "../types";

/**
 * 聊天会话配置选项接口
 */
interface UseChatSessionOptions {
  sessionId: string;     // 会话 ID
  project: string;       // 项目名称
  maxRetries?: number;   // SSE 最大重试次数
}

/**
 * 聊天会话管理 Hook
 * 整合 SSE 连接、状态管理、审批处理的高级 Hook
 *
 * @param options - 配置选项
 * @returns 聊天会话的状态和控制方法
 */
export function useChatSession({ sessionId, project, maxRetries = 3 }: UseChatSessionOptions) {
  // 待审批事件状态
  const [pendingApproval, setPendingApproval] = useState<ApprovalRequiredEvent | null>(null);

  // 从 useChatStore 获取状态和控制方法
  const {
    state,            // 聊天状态
    agentEvents,      // Agent 启动事件列表
    handleEvent,      // 事件处理函数
    setConnected,     // 设置连接状态
    setReconnecting,  // 设置重连状态
    setError,         // 设置错误
    reset,            // 重置状态
  } = useChatStore(sessionId, project);

  /**
   * 发送消息
   * 重置状态，建立 SSE 连接，开始接收 Agent 响应
   *
   * @param message - 用户消息内容
   * @returns SSE 连接对象
   */
  const sendMessage = useCallback(
    (message: string) => {
      reset();  // 重置之前的状态
      setPendingApproval(null);  // 清除待审批

      // 建立 SSE 连接
      const sse = useSSE({
        sessionId,
        project,
        message,
        maxRetries,
        onEvent: handleEvent,      // 每个事件触发状态更新
        onComplete: () => setConnected(false),  // 完成时断开连接
        onError: (err) => setError(err),        // 错误时记录
      });

      return sse;
    },
    [sessionId, project, maxRetries]
  );

  /**
   * 批准操作
   * 用户确认审批后清除待审批状态
   */
  const approveAction = useCallback(async () => {
    if (!pendingApproval) return;  // 无待审批则跳过
    setPendingApproval(null);      // 清除待审批
    // TODO: 向后端发送批准响应
  }, [pendingApproval]);

  /**
   * 拒绝操作
   * 用户拒绝审批后清除待审批状态
   */
  const rejectAction = useCallback(async () => {
    if (!pendingApproval) return;  // 无待审批则跳过
    setPendingApproval(null);      // 清除待审批
    // TODO: 向后端发送拒绝响应
  }, [pendingApproval]);

  // 返回状态和控制方法
  return {
    state,              // 聊天状态
    agentEvents,        // Agent 事件列表
    pendingApproval,    // 待审批事件
    sendMessage,        // 发送消息
    approveAction,      // 批准操作
    rejectAction,       // 拒绝操作
    reset,              // 重置状态
  };
}
