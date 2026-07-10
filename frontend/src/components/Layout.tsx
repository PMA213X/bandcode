/**
 * Layout.tsx - 布局组件
 * 功能：提供应用整体布局框架，包含标题栏、内容区、状态栏
 *       支持视图切换（对话/设置/记忆）和快捷键导航
 */

// 导入 React
import React, { useState } from "react";
// 导入 Ink 终端 UI 组件和 Hooks
import { Box, Text, useInput, useApp } from "ink";

/**
 * 视图模式类型定义
 * chat: 对话视图
 * settings: 设置视图
 * memory: 记忆视图
 */
type ViewMode = "chat" | "settings" | "memory";

/**
 * Layout 组件属性接口
 * children: 子组件内容
 * currentView: 当前激活的视图模式，默认为 "chat"
 * onViewChange: 视图切换回调函数
 */
interface LayoutProps {
  children: React.ReactNode;
  currentView?: ViewMode;
  onViewChange?: (view: ViewMode) => void;
}

/**
 * 视图标签映射表
 * 将视图模式转换为中文显示标签
 */
const VIEW_LABELS: Record<ViewMode, string> = {
  chat: "对话",      // 对话视图标签
  settings: "设置",  // 设置视图标签
  memory: "记忆",    // 记忆视图标签
};

/**
 * 视图快捷键映射表
 * 数字键 1/2/3 对应切换到不同视图
 */
const VIEW_SHORTCUTS: Record<string, ViewMode> = {
  "1": "chat",      // 按 1 切换到对话视图
  "2": "settings",  // 按 2 切换到设置视图
  "3": "memory",    // 按 3 切换到记忆视图
};

/**
 * Layout 布局主组件
 * 提供三段式布局：标题栏 + 内容区 + 状态栏
 */
export function Layout({ children, currentView = "chat", onViewChange }: LayoutProps) {
  // 获取 Ink 应用退出方法
  const { exit } = useApp();

  /**
   * 键盘输入处理
   * 处理快捷键：Ctrl+C 退出，数字键切换视图
   */
  useInput((inputChar, key) => {
    // Ctrl+C：退出应用
    if (key.ctrl && inputChar === "c") {
      exit();
      return;
    }

    // 数字键：切换视图
    if (VIEW_SHORTCUTS[inputChar]) {
      onViewChange?.(VIEW_SHORTCUTS[inputChar]);
    }
  });

  /**
   * 渲染布局结构
   * 三段式布局：标题栏 + 内容区 + 状态栏
   */
  return (
    // 主容器：垂直布局，占满终端高度
    <Box flexDirection="column" height="100%">
      {/* 顶部标题栏：显示应用名称和当前视图 */}
      <Box
        flexDirection="row"           // 水平布局
        justifyContent="space-between" // 两端对齐
        alignItems="center"           // 垂直居中
        paddingX={1}                  // 左右内边距
        borderBottom                   // 底部边框
      >
        {/* 应用名称：青色加粗显示 */}
        <Text color="cyan" bold>
          BandCode
        </Text>
        {/* 当前视图和快捷键提示：灰色显示 */}
        <Text color="gray">
          {VIEW_LABELS[currentView]} | 1:对话 2:设置 3:记忆 Ctrl+C:退出
        </Text>
      </Box>

      {/* 主内容区域：垂直布局，占满剩余空间 */}
      <Box flexDirection="column" flexGrow={1} overflow="hidden">
        {children} {/* 渲染子组件 */}
      </Box>

      {/* 底部状态栏：显示版本号和当前时间 */}
      <Box
        flexDirection="row"           // 水平布局
        justifyContent="space-between" // 两端对齐
        paddingX={1}                  // 左右内边距
        borderTop                     // 顶部边框
      >
        {/* 版本号：灰色暗淡显示 */}
        <Text color="gray" dimColor>
          v1.0.0
        </Text>
        {/* 当前时间：灰色暗淡显示，中文格式 */}
        <Text color="gray" dimColor>
          {new Date().toLocaleTimeString("zh-CN")}
        </Text>
      </Box>
    </Box>
  );
}

/**
 * StatusBar 状态栏组件属性接口
 */
interface StatusBarProps {
  project?: string;      // 项目名称
  session?: string;      // 会话ID
  isConnected?: boolean; // 是否已连接
}

/**
 * StatusBar 状态栏组件
 * 显示项目、会话和连接状态信息
 */
export function StatusBar({ project, session, isConnected }: StatusBarProps) {
  return (
    // 水平布局，两端对齐
    <Box flexDirection="row" justifyContent="space-between" paddingX={1}>
      {/* 项目名称：灰色显示，未选择时显示提示 */}
      <Text color="gray" dimColor>
        项目: {project || "未选择"}
      </Text>
      {/* 会话ID：截取前8位显示，无会话时显示提示 */}
      <Text color="gray" dimColor>
        会话: {session ? session.slice(0, 8) + "..." : "无"}
      </Text>
      {/* 连接状态：已连接显示绿色，断开显示红色 */}
      <Text color={isConnected ? "green" : "red"}>
        {isConnected ? "● 已连接" : "○ 断开"}
      </Text>
    </Box>
  );
}

/**
 * TabBar 标签栏组件属性接口
 */
interface TabBarProps {
  tabs: Array<{ key: string; label: string; icon?: string }>; // 标签配置数组
  activeTab: string;   // 当前激活的标签key
  onTabChange: (key: string) => void; // 标签切换回调
}

/**
 * TabBar 标签栏组件
 * 渲染水平排列的标签，支持图标和选中状态
 */
export function TabBar({ tabs, activeTab, onTabChange }: TabBarProps) {
  return (
    // 水平布局，左内边距
    <Box flexDirection="row" paddingX={1}>
      {/* 遍历渲染每个标签 */}
      {tabs.map((tab) => (
        // 标签容器：右侧外边距
        <Box key={tab.key} marginRight={2}>
          {/* 标签文本：选中时青色加粗，未选中时灰色 */}
          <Text
            color={tab.key === activeTab ? "cyan" : "gray"}
            bold={tab.key === activeTab}
          >
            {/* 图标（如果有） */}
            {tab.icon ? `${tab.icon} ` : ""}
            {/* 标签文本 */}
            {tab.label}
          </Text>
        </Box>
      ))}
    </Box>
  );
}

// 导出 Layout 组件作为默认导出
export default Layout;
