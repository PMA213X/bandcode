/**
 * Chat.tsx - 聊天界面组件
 * 功能：消息列表展示、用户输入框、SSE流式消息输出、Agent状态显示、命令面板
 */

// 导入 React 核心 Hooks
import React, { useState, useEffect, useRef, useCallback } from "react";
// 导入 Ink 终端 UI 组件和 Hooks
import { Box, Text, useInput, useApp } from "ink";
// 导入 Agent 状态列表组件，用于显示当前运行的 Agent
import { AgentStatusList } from "./AgentStatus";
// 导入 SSE Hook，用于处理服务器推送事件
import { useSSE } from "../hooks/useSSE";
// 导入命令面板相关组件和 Hook
import { useCommands } from "../hooks/useCommands";
import CommandPalette from "./CommandPalette";
import FileSelector from "./FileSelector";
// 导入类型定义
import MemoryView from "./MemoryView";
import type { ChatMessage, SSEEvent, AgentStartEvent } from "../types";

/**
 * Chat 组件属性接口
 * sessionId: 会话ID，用于标识当前对话
 * project: 项目名称，用于标识当前项目
 */
interface ChatProps {
  sessionId?: string;
  project?: string;
}

/**
 * Agent 颜色映射表
 * 为不同类型的 Agent 分配不同的终端显示颜色
 */
const AGENT_COLORS: Record<string, string> = {
  constraint: "gray",      // 约束检索 Agent - 灰色
  planner: "blue",         // 规划调度 Agent - 蓝色
  "simple-coder": "green", // 简单编码 Agent - 绿色
  "complex-coder": "magenta", // 复杂编码 Agent - 品红色
  tester: "yellow",        // 测试验证 Agent - 黄色
  review: "red",           // 约束审查 Agent - 红色
};

/**
 * 角色图标映射表
 * user: 用户消息前缀 ">>>"
 * assistant: 助手消息前缀 "<<<"
 */
const ROLE_ICONS: Record<string, string> = {
  user: ">>>",
  assistant: "<<<",
};

/**
 * Chat 聊天界面主组件
 * 管理消息状态、输入处理、SSE 连接和 UI 渲染
 */
export function Chat({ sessionId = "default", project = "default" }: ChatProps) {
  // 消息列表状态，存储所有对话消息
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  // 用户输入内容状态
  const [input, setInput] = useState("");
  // 是否正在接收 SSE 流式数据
  const [isStreaming, setIsStreaming] = useState(false);
  // 当前正在流式输出的消息内容（临时存储）
  const [currentMessage, setCurrentMessage] = useState("");
  // Agent 启动事件列表，记录参与处理的 Agent
  const [agentEvents, setAgentEvents] = useState<AgentStartEvent[]>([]);
  // 当前正在执行的 Agent 名称
  const [currentAgent, setCurrentAgent] = useState<string>("");
  // 消息列表底部引用，用于自动滚动
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // 当前视图状态
  const [currentView, setCurrentView] = useState<string>("chat");

  // 获取 Ink 应用退出方法
  const { exit } = useApp();

  // 导航函数，用于处理命令面板的命令执行
  const navigate = useCallback((view: string) => {
    switch (view) {
      case 'memory':
      case 'memory-global':
      case 'memory-project':
        setCurrentView('memory');
        break;
      case 'settings':
        setCurrentView('settings');
        break;
      default:
        console.log(`Navigate to: ${view}`);
    }
  }, []);

  // 命令面板 Hook
  const {
    showCommandPalette,
    commandQuery,
    showFileSelector,
    fileQuery,
    commands,
    handleInputChange,
    handleCommandSelect,
    handleFileSelect,
    closeCommandPalette,
    closeFileSelector,
  } = useCommands(navigate);

  /**
   * 处理消息发送
   * 创建用户消息对象并添加到消息列表，同时触发 SSE 连接
   */
  const handleSend = useCallback(
    (content: string) => {
      // 空消息或正在流式传输时不允许发送
      if (!content.trim() || isStreaming) return;

      // 构造用户消息对象
      const userMessage: ChatMessage = {
        id: Date.now(),                    // 使用时间戳作为消息ID
        role: "user",                      // 角色：用户
        content: content.trim(),           // 消息内容（去除首尾空格）
        created_at: new Date().toISOString(), // 创建时间
      };

      // 将用户消息添加到消息列表
      setMessages((prev) => [...prev, userMessage]);
      // 清空输入框
      setInput("");
      // 标记开始流式传输
      setIsStreaming(true);
      // 清空临时消息内容
      setCurrentMessage("");
      // 清空 Agent 事件列表
      setAgentEvents([]);
    },
    [isStreaming] // 依赖：isStreaming 状态
  );

  /**
   * 使用 SSE Hook 建立服务器推送连接
   * 监听各种事件类型并更新组件状态
   */
  const { events, isConnected, disconnect } = useSSE({
    sessionId,    // 会话ID
    project,      // 项目名称
    message: input, // 发送的消息内容
    // SSE 事件回调处理
    onEvent: (event: SSEEvent) => {
      if (event.type === "agent_start") {
        // Agent 启动事件：记录 Agent 信息
        const data = event.data as { agent: string; status: string };
        setAgentEvents((prev) => [...prev, data]); // 添加到 Agent 事件列表
        setCurrentAgent(data.agent);               // 设置当前 Agent
      } else if (event.type === "code" || event.type === "tool_call") {
        // 代码/工具调用事件：追加内容到当前消息
        const data = event.data as { content?: string; file?: string };
        if (data.content) {
          setCurrentMessage((prev) => prev + data.content); // 追加内容（打字机效果）
        }
      } else if (event.type === "done") {
        // 完成事件：结束流式传输，保存助手消息
        setIsStreaming(false);   // 标记流式传输结束
        setCurrentAgent("");     // 清空当前 Agent
        if (currentMessage) {
          // 构造助手消息对象
          const assistantMessage: ChatMessage = {
            id: Date.now(),
            role: "assistant",           // 角色：助手
            content: currentMessage,     // 使用累积的消息内容
            created_at: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, assistantMessage]); // 添加到消息列表
          setCurrentMessage(""); // 清空临时消息
        }
      } else if (event.type === "error") {
        // 错误事件：显示错误信息
        setIsStreaming(false);   // 结束流式传输
        setCurrentAgent("");     // 清空当前 Agent
        const data = event.data as { message: string };
        setCurrentMessage(`[错误] ${data.message}`); // 显示错误消息
      }
    },
  });

  /**
   * 键盘输入处理
   * 处理快捷键和普通字符输入
   */
  useInput((inputChar, key) => {
    // Ctrl+C：断开 SSE 连接并退出应用
    if (key.ctrl && inputChar === "c") {
      disconnect();
      exit();
      return;
    }

    // 命令面板或文件选择器打开时，不处理普通输入
    if (showCommandPalette || showFileSelector) {
      return;
    }

    // 回车键：发送消息
    if (key.return) {
      handleSend(input);
    }
    // 退格键：删除最后一个字符
    else if (key.backspace) {
      setInput((prev) => {
        const newInput = prev.slice(0, -1);
        handleInputChange(newInput);
        return newInput;
      });
    }
    // 普通字符：追加到输入内容（排除 Ctrl 和 Meta 组合键）
    else if (!key.ctrl && !key.meta) {
      setInput((prev) => {
        const newInput = prev + inputChar;
        handleInputChange(newInput);
        return newInput;
      });
    }
  });

  /**
   * 渲染聊天界面
   * 布局：消息列表 + 分隔线 + 输入框
   */
  // Memory 视图
  if (currentView === 'memory') {
    return <MemoryView onClose={() => setCurrentView('chat')} />;
  }

  return (
    <Box flexDirection="column" height="100%">
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
        {isStreaming && !currentMessage && (
          <Box paddingX={1}>
            <Text color="yellow">⟳ 正在处理...</Text>
          </Box>
        )}
        <Box ref={messagesEndRef} />
      </Box>
      {showCommandPalette && (
        <CommandPalette
          commands={commands}
          query={commandQuery}
          onSelect={handleCommandSelect}
          onClose={closeCommandPalette}
        />
      )}
      {showFileSelector && (
        <FileSelector
          query={fileQuery}
          onSelect={(file) => {
            const path = handleFileSelect(file);
            setInput((prev) => prev.replace(/@[^@]*$/, path));
          }}
          onClose={closeFileSelector}
        />
      )}
      <Box>
        <Text color="gray">{"─".repeat(80)}</Text>
      </Box>
      <Box paddingX={1} paddingY={0}>
        <Text color="cyan">{">>> "}</Text>
        <Text color="white">{input}</Text>
        <Text color="gray">{"█"}</Text>
      </Box>
    </Box>
  );
}

/**
 * MessageBubble 消息气泡组件属性接口
 */
interface MessageBubbleProps {
  message: ChatMessage;
}

/**
 * MessageBubble 消息气泡组件
 * 渲染单条消息，根据角色和 Agent 类型显示不同颜色
 */
function MessageBubble({ message }: MessageBubbleProps) {
  // 判断是否为用户消息
  const isUser = message.role === "user";
  // 获取角色对应的图标
  const icon = ROLE_ICONS[message.role];
  // 根据 Agent 类型或角色确定颜色
  const agentColor = message.agent
    ? AGENT_COLORS[message.agent] || "white" // 有 Agent 时使用 Agent 颜色
    : isUser
    ? "cyan"   // 用户消息使用青色
    : "green"; // 助手消息使用绿色

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

// 导出 Chat 组件作为默认导出
export default Chat;
