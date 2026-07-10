import React, { useState, useEffect, useRef, useCallback } from "react";
import { Box, Text, useInput, useApp } from "ink";
import { AgentStatusList } from "./AgentStatus";
import { useSSE } from "../hooks/useSSE";
import type { ChatMessage, SSEEvent, AgentStartEvent } from "../types";

interface ChatProps {
  sessionId: string;
  project: string;
}

const AGENT_COLORS: Record<string, string> = {
  constraint: "gray",
  planner: "blue",
  "simple-coder": "green",
  "complex-coder": "magenta",
  tester: "yellow",
  review: "red",
};

const ROLE_ICONS: Record<string, string> = {
  user: ">>>",
  assistant: "<<<",
};

export function Chat({ sessionId, project }: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentMessage, setCurrentMessage] = useState("");
  const [agentEvents, setAgentEvents] = useState<AgentStartEvent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { exit } = useApp();

  const handleSend = useCallback(
    (content: string) => {
      if (!content.trim() || isStreaming) return;

      const userMessage: ChatMessage = {
        id: Date.now(),
        role: "user",
        content: content.trim(),
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsStreaming(true);
      setCurrentMessage("");
      setAgentEvents([]);
    },
    [isStreaming]
  );

  const { events, isConnected, disconnect } = useSSE({
    sessionId,
    project,
    message: input,
    onEvent: (event: SSEEvent) => {
      if (event.type === "agent_start") {
        const data = event.data as { agent: string; status: string };
        setAgentEvents((prev) => [...prev, data]);
        setCurrentAgent(data.agent);
      } else if (event.type === "code" || event.type === "tool_call") {
        const data = event.data as { content?: string; file?: string };
        if (data.content) {
          setCurrentMessage((prev) => prev + data.content);
        }
      } else if (event.type === "done") {
        setIsStreaming(false);
        setCurrentAgent("");
        if (currentMessage) {
          const assistantMessage: ChatMessage = {
            id: Date.now(),
            role: "assistant",
            content: currentMessage,
            created_at: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setCurrentMessage("");
        }
      } else if (event.type === "error") {
        setIsStreaming(false);
        setCurrentAgent("");
        const data = event.data as { message: string };
        setCurrentMessage(`[错误] ${data.message}`);
      }
    },
  });

  useInput((inputChar, key) => {
    if (key.ctrl && inputChar === "c") {
      disconnect();
      exit();
      return;
    }

    if (key.return) {
      handleSend(input);
    } else if (key.backspace) {
      setInput((prev) => prev.slice(0, -1));
    } else if (!key.ctrl && !key.meta) {
      setInput((prev) => prev + inputChar);
    }
  });

  return (
    <Box flexDirection="column" height="100%">
      {/* 消息列表区域 */}
      <Box flexDirection="column" flexGrow={1} overflow="hidden">
        {messages.length === 0 && !isStreaming && (
          <Box padding={1}>
            <Text color="gray" italic>
              输入消息开始对话... (Ctrl+C 退出)
            </Text>
          </Box>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {/* 正在流式输出的消息 */}
        {isStreaming && currentMessage && (
          <Box flexDirection="column" paddingX={1}>
            {agentEvents.length > 0 && (
              <Box marginBottom={1}>
                <AgentStatusList
                  events={agentEvents}
                  currentAgent={currentAgent}
                />
              </Box>
            )}
            <Box>
              <Text color="cyan">{ROLE_ICONS.assistant} </Text>
              <Text color="white">{currentMessage}</Text>
              <Text color="gray">{"█"}</Text>
            </Box>
          </Box>
        )}

        {/* 加载指示器 */}
        {isStreaming && !currentMessage && (
          <Box paddingX={1}>
            <Text color="yellow">⟳ 正在处理...</Text>
          </Box>
        )}

        <Box ref={messagesEndRef} />
      </Box>

      {/* 分隔线 */}
      <Box>
        <Text color="gray">{"─".repeat(80)}</Text>
      </Box>

      {/* 输入框区域 */}
      <Box paddingX={1} paddingY={0}>
        <Text color="cyan">{">>> "} </Text>
        <Text color="white">{input}</Text>
        <Text color="gray">{"█"}</Text>
      </Box>
    </Box>
  );
}

interface MessageBubbleProps {
  message: ChatMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const icon = ROLE_ICONS[message.role];
  const agentColor = message.agent
    ? AGENT_COLORS[message.agent] || "white"
    : isUser
    ? "cyan"
    : "green";

  return (
    <Box flexDirection="column" paddingX={1} marginBottom={1}>
      <Box>
        <Text color={agentColor} bold>
          {icon}{" "}
        </Text>
        {message.agent && (
          <Text color={agentColor} dimColor>
            [{message.agent}]{" "}
          </Text>
        )}
        <Text color="white">{message.content}</Text>
      </Box>
    </Box>
  );
}

export default Chat;
