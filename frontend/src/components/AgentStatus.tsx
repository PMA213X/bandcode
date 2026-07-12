// 导入 React 库
import React from "react";
// 导入 Ink 组件：Box 用于布局，Text 用于文本显示
import { Box, Text } from "ink";
// 导入 Agent 启动事件类型
import type { AgentStartEvent } from "../types";

/**
 * Agent 状态组件属性接口
 */
interface AgentStatusProps {
  agent: string;      // Agent 名称（如 planner、simple-coder）
  status: string;     // Agent 状态描述
  isActive: boolean;  // 是否为当前活跃的 Agent
}

/**
 * Agent 颜色映射表
 * 不同 Agent 使用不同颜色显示，便于区分
 */
const AGENT_COLORS: Record<string, string> = {
  constraint: "gray",        // 约束检索：灰色
  planner: "blue",           // 规划调度：蓝色
  "simple-coder": "green",   // 简单编码：绿色
  "complex-coder": "magenta",// 复杂编码：品红色
  tester: "yellow",          // 测试验证：黄色
  review: "red",             // 约束审查：红色
};

/**
 * Agent 中文标签映射表
 * 将英文 Agent 名称转换为中文显示
 */
const AGENT_LABELS: Record<string, string> = {
  constraint: "约束检索",      // Constraint Agent
  planner: "规划调度",         // Planner Agent
  "simple-coder": "简单编码",  // SimpleCoder Agent
  "complex-coder": "复杂编码", // ComplexCoder Agent
  tester: "测试验证",          // Tester Agent
  review: "约束审查",          // Review Agent
};

/**
 * Agent 状态显示组件
 * 显示单个 Agent 的运行状态，使用颜色和图标区分
 *
 * @param agent - Agent 名称
 * @param status - 状态描述
 * @param isActive - 是否活跃
 */
export function AgentStatus({ agent, status, isActive }: AgentStatusProps) {
  // 获取 Agent 对应的颜色，默认白色
  const color = AGENT_COLORS[agent] || "white";
  // 获取 Agent 对应的中文标签，如果没有则使用原名
  const label = AGENT_LABELS[agent] || agent;
  // 活跃状态显示旋转图标，否则显示完成图标
  const icon = isActive ? "⟳" : "✓";

  return (
    <Box>
      <Text color={color}>
        {icon} [{label}] {status}
      </Text>
    </Box>
  );
}

/**
 * Agent 状态列表组件属性接口
 */
interface AgentStatusListProps {
  events: AgentStartEvent[];  // Agent 启动事件列表
  currentAgent?: string;      // 当前活跃的 Agent
}

/**
 * Agent 状态列表组件
 * 显示所有 Agent 的运行历史，去重后按顺序排列
 *
 * @param events - Agent 启动事件数组
 * @param currentAgent - 当前活跃的 Agent 名称
 */
export function AgentStatusList({ events, currentAgent }: AgentStatusListProps) {
  // 使用 Set 去重，避免重复显示同一个 Agent
  const seen = new Set<string>();

  return (
    <Box flexDirection="column">
      {events
        .filter((e) => {
          // 如果已经显示过这个 Agent，跳过
          if (seen.has(e.agent)) return false;
          seen.add(e.agent);  // 标记为已显示
          return true;
        })
        .map((e, i) => (
          // 渲染每个 Agent 的状态
          <AgentStatus
            key={`${e.agent}-${i}`}  // 唯一 key
            agent={e.agent}          // Agent 名称
            status={e.status}        // 状态描述
            isActive={e.agent === currentAgent}  // 是否为当前活跃 Agent
          />
        ))}
    </Box>
  );
}

// 默认导出
export default AgentStatus;
