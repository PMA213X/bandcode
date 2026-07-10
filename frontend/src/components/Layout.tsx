import React, { useState } from "react";
import { Box, Text, useInput, useApp } from "ink";

type ViewMode = "chat" | "settings" | "memory";

interface LayoutProps {
  children: React.ReactNode;
  currentView?: ViewMode;
  onViewChange?: (view: ViewMode) => void;
}

const VIEW_LABELS: Record<ViewMode, string> = {
  chat: "对话",
  settings: "设置",
  memory: "记忆",
};

const VIEW_SHORTCUTS: Record<string, ViewMode> = {
  "1": "chat",
  "2": "settings",
  "3": "memory",
};

export function Layout({ children, currentView = "chat", onViewChange }: LayoutProps) {
  const { exit } = useApp();

  useInput((inputChar, key) => {
    if (key.ctrl && inputChar === "c") {
      exit();
      return;
    }

    if (VIEW_SHORTCUTS[inputChar]) {
      onViewChange?.(VIEW_SHORTCUTS[inputChar]);
    }
  });

  return (
    <Box flexDirection="column" height="100%">
      {/* 顶部标题栏 */}
      <Box
        flexDirection="row"
        justifyContent="space-between"
        alignItems="center"
        paddingX={1}
        borderBottom
      >
        <Text color="cyan" bold>
          BandCode
        </Text>
        <Text color="gray">
          {VIEW_LABELS[currentView]} | 1:对话 2:设置 3:记忆 Ctrl+C:退出
        </Text>
      </Box>

      {/* 主内容区域 */}
      <Box flexDirection="column" flexGrow={1} overflow="hidden">
        {children}
      </Box>

      {/* 底部状态栏 */}
      <Box
        flexDirection="row"
        justifyContent="space-between"
        paddingX={1}
        borderTop
      >
        <Text color="gray" dimColor>
          v1.0.0
        </Text>
        <Text color="gray" dimColor>
          {new Date().toLocaleTimeString("zh-CN")}
        </Text>
      </Box>
    </Box>
  );
}

interface StatusBarProps {
  project?: string;
  session?: string;
  isConnected?: boolean;
}

export function StatusBar({ project, session, isConnected }: StatusBarProps) {
  return (
    <Box flexDirection="row" justifyContent="space-between" paddingX={1}>
      <Text color="gray" dimColor>
        项目: {project || "未选择"}
      </Text>
      <Text color="gray" dimColor>
        会话: {session ? session.slice(0, 8) + "..." : "无"}
      </Text>
      <Text color={isConnected ? "green" : "red"}>
        {isConnected ? "● 已连接" : "○ 断开"}
      </Text>
    </Box>
  );
}

interface TabBarProps {
  tabs: Array<{ key: string; label: string; icon?: string }>;
  activeTab: string;
  onTabChange: (key: string) => void;
}

export function TabBar({ tabs, activeTab, onTabChange }: TabBarProps) {
  return (
    <Box flexDirection="row" paddingX={1}>
      {tabs.map((tab) => (
        <Box key={tab.key} marginRight={2}>
          <Text
            color={tab.key === activeTab ? "cyan" : "gray"}
            bold={tab.key === activeTab}
          >
            {tab.icon ? `${tab.icon} ` : ""}
            {tab.label}
          </Text>
        </Box>
      ))}
    </Box>
  );
}

export default Layout;
