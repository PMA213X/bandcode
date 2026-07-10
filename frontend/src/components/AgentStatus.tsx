import React from "react";
import { Box, Text } from "ink";
import type { AgentStartEvent } from "../types";

interface AgentStatusProps {
  agent: string;
  status: string;
  isActive: boolean;
}

const AGENT_COLORS: Record<string, string> = {
  constraint: "gray",
  planner: "blue",
  "simple-coder": "green",
  "complex-coder": "magenta",
  tester: "yellow",
  review: "red",
};

const AGENT_LABELS: Record<string, string> = {
  constraint: "约束检索",
  planner: "规划调度",
  "simple-coder": "简单编码",
  "complex-coder": "复杂编码",
  tester: "测试验证",
  review: "约束审查",
};

export function AgentStatus({ agent, status, isActive }: AgentStatusProps) {
  const color = AGENT_COLORS[agent] || "white";
  const label = AGENT_LABELS[agent] || agent;
  const icon = isActive ? "⟳" : "✓";

  return (
    <Box>
      <Text color={color}>
        {icon} [{label}] {status}
      </Text>
    </Box>
  );
}

interface AgentStatusListProps {
  events: AgentStartEvent[];
  currentAgent?: string;
}

export function AgentStatusList({ events, currentAgent }: AgentStatusListProps) {
  const seen = new Set<string>();

  return (
    <Box flexDirection="column">
      {events
        .filter((e) => {
          if (seen.has(e.agent)) return false;
          seen.add(e.agent);
          return true;
        })
        .map((e, i) => (
          <AgentStatus
            key={`${e.agent}-${i}`}
            agent={e.agent}
            status={e.status}
            isActive={e.agent === currentAgent}
          />
        ))}
    </Box>
  );
}

export default AgentStatus;
