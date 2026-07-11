/**
 * Settings.tsx - 设置面板组件
 * 功能：全中文6大类39项设置展示与修改
 */

import React, { useState, useEffect, useCallback } from "react";
import { Box, Text, useInput, useApp } from "ink";
import { COLORS, ICONS } from "../styles/colors";

/**
 * 设置分类接口
 */
interface SettingsCategory {
  name: string;
  items: SettingsItem[];
}

/**
 * 设置项接口
 */
interface SettingsItem {
  key: string;
  label: string;
  type: "text" | "number" | "boolean" | "select";
  value: any;
  options?: string[];
  description?: string;
}

/**
 * Settings组件属性接口
 */
interface SettingsProps {
  onSave?: (settings: Record<string, any>) => void;
  initialSettings?: Record<string, any>;
}

/**
 * 默认设置数据
 */
const DEFAULT_SETTINGS: SettingsCategory[] = [
  {
    name: "模型设置",
    items: [
      { key: "default_model", label: "默认模型", type: "text", value: "mimo-v2.5-pro", description: "默认使用的LLM模型" },
      { key: "base_url", label: "Base URL", type: "text", value: "http://localhost:8000/v1", description: "LLM API基础地址" },
      { key: "api_key", label: "API Key", type: "text", value: "", description: "LLM API密钥" },
      { key: "planner_model", label: "Planner 模型", type: "text", value: "mimo-v2.5-pro", description: "规划调度Agent使用的模型" },
      { key: "temperature", label: "温度参数", type: "number", value: 0.1, description: "LLM生成温度，0-1之间" },
      { key: "max_tokens", label: "最大Token数", type: "number", value: 4096, description: "单次生成最大Token数" },
      { key: "timeout", label: "超时时间(秒)", type: "number", value: 60, description: "LLM请求超时时间" },
      { key: "max_retries", label: "最大重试次数", type: "number", value: 3, description: "LLM请求失败重试次数" },
    ],
  },
  {
    name: "Agent 设置",
    items: [
      { key: "default_agent", label: "默认Agent", type: "select", value: "planner", options: ["planner", "simple-coder", "complex-coder"], description: "默认使用的Agent" },
      { key: "approval_mode", label: "审批模式", type: "boolean", value: true, description: "高风险操作是否需要用户确认" },
      { key: "max_iterations", label: "最大迭代次数", type: "number", value: 10, description: "Agent最大迭代次数" },
      { key: "auto_retry", label: "自动重试", type: "boolean", value: true, description: "失败时是否自动重试" },
      { key: "verbose_logging", label: "详细日志", type: "boolean", value: false, description: "是否输出详细日志" },
      { key: "agent_timeout", label: "Agent超时(秒)", type: "number", value: 120, description: "单个Agent执行超时时间" },
      { key: "parallel_agents", label: "并行Agent数", type: "number", value: 1, description: "同时运行的Agent数量" },
    ],
  },
  {
    name: "Memory 设置",
    items: [
      { key: "auto_update_memory", label: "自动更新Memory", type: "boolean", value: true, description: "是否自动更新Memory" },
      { key: "memory_compression", label: "Memory压缩", type: "boolean", value: true, description: "是否启用Memory压缩" },
      { key: "compression_threshold", label: "压缩阈值", type: "number", value: 1000, description: "Memory条目数超过此值时压缩" },
      { key: "global_memory_path", label: "Global Memory路径", type: "text", value: "memory/global", description: "全局Memory存储路径" },
      { key: "project_memory_path", label: "Project Memory路径", type: "text", value: "memory/project", description: "项目Memory存储路径" },
      { key: "task_memory_path", label: "Task Memory路径", type: "text", value: "memory/task", description: "任务Memory存储路径" },
      { key: "session_memory_path", label: "Session Memory路径", type: "text", value: "memory/session", description: "会话Memory存储路径" },
    ],
  },
  {
    name: "Workflow 设置",
    items: [
      { key: "enable_constraint_search", label: "开启约束智能检索", type: "boolean", value: true, description: "是否启用Constraint Agent" },
      { key: "enable_auto_review", label: "开启自动约束检查", type: "boolean", value: true, description: "是否启用Review Agent" },
      { key: "auto_fix", label: "自动修正", type: "boolean", value: true, description: "Review失败时是否自动修正" },
      { key: "max_review_iterations", label: "最大Review次数", type: "number", value: 3, description: "Review最大迭代次数" },
      { key: "enable_checkpoint", label: "开启快照管理", type: "boolean", value: true, description: "是否启用Checkpoint" },
      { key: "checkpoint_interval", label: "快照间隔(秒)", type: "number", value: 300, description: "自动创建快照的间隔" },
      { key: "enable_rollback", label: "开启回滚功能", type: "boolean", value: true, description: "是否支持快照回滚" },
    ],
  },
  {
    name: "RAG 设置",
    items: [
      { key: "knowledge_path", label: "知识库路径", type: "text", value: "knowledge", description: "知识库文档目录" },
      { key: "retrieval_count", label: "检索数量", type: "number", value: 5, description: "每次检索返回的文档数量" },
      { key: "chunk_size", label: "分块大小", type: "number", value: 500, description: "文档分块大小(字符)" },
      { key: "chunk_overlap", label: "分块重叠", type: "number", value: 50, description: "分块重叠大小(字符)" },
      { key: "embedding_model", label: "Embedding模型", type: "text", value: "text-embedding-ada-002", description: "向量化使用的模型" },
      { key: "enable_rerank", label: "开启重排序", type: "boolean", value: false, description: "是否对检索结果重排序" },
    ],
  },
  {
    name: "Tool 设置",
    items: [
      { key: "tools_path", label: "工具目录", type: "text", value: "tools", description: "自定义工具目录" },
      { key: "enable_builtins", label: "启用内置工具", type: "boolean", value: true, description: "是否启用内置工具" },
      { key: "read_permission", label: "读取权限", type: "select", value: "allow", options: ["allow", "deny", "ask"], description: "文件读取权限" },
      { key: "write_permission", label: "写入权限", type: "select", value: "allow", options: ["allow", "deny", "ask"], description: "文件写入权限" },
      { key: "bash_permission", label: "Bash权限", type: "select", value: "ask", options: ["allow", "deny", "ask"], description: "Bash命令执行权限" },
      { key: "edit_permission", label: "编辑权限", type: "select", value: "allow", options: ["allow", "deny", "ask"], description: "文件编辑权限" },
      { key: "max_file_size", label: "最大文件大小(KB)", type: "number", value: 1024, description: "允许操作的最大文件大小" },
    ],
  },
];

/**
 * Settings 设置面板主组件
 */
export function Settings({ onSave, initialSettings }: SettingsProps) {
  // 当前选中的分类索引
  const [selectedCategory, setSelectedCategory] = useState(0);
  // 当前选中的设置项索引（在当前分类内）
  const [selectedItem, setSelectedItem] = useState(0);
  // 所有设置数据
  const [settings, setSettings] = useState<SettingsCategory[]>(DEFAULT_SETTINGS);
  // 是否处于编辑模式
  const [isEditing, setIsEditing] = useState(false);
  // 编辑缓冲区
  const [editBuffer, setEditBuffer] = useState("");
  // 是否有未保存的更改
  const [hasChanges, setHasChanges] = useState(false);

  // 获取Ink应用退出方法
  const { exit } = useApp();

  /**
   * 获取当前分类的设置项
   */
  const currentItems = settings[selectedCategory]?.items || [];

  /**
   * 获取当前选中的设置项
   */
  const currentItem = currentItems[selectedItem];

  /**
   * 处理键盘输入
   */
  useInput((inputChar, key) => {
    // Ctrl+C：退出
    if (key.ctrl && inputChar === "c") {
      exit();
      return;
    }

    // Escape：退出编辑模式或退出设置
    if (key.escape) {
      if (isEditing) {
        setIsEditing(false);
        setEditBuffer("");
      } else {
        exit();
      }
      return;
    }

    // 编辑模式下的处理
    if (isEditing) {
      if (key.return) {
        // 回车：确认编辑
        handleEditConfirm();
      } else if (key.backspace) {
        // 退格：删除字符
        setEditBuffer((prev) => prev.slice(0, -1));
      } else if (!key.ctrl && !key.meta) {
        // 普通字符：追加到缓冲区
        setEditBuffer((prev) => prev + inputChar);
      }
      return;
    }

    // 非编辑模式下的导航
    if (key.upArrow) {
      // 上箭头：选择上一项
      setSelectedItem((prev) => (prev > 0 ? prev - 1 : currentItems.length - 1));
    } else if (key.downArrow) {
      // 下箭头：选择下一项
      setSelectedItem((prev) => (prev < currentItems.length - 1 ? prev + 1 : 0));
    } else if (key.leftArrow) {
      // 左箭头：选择上一分类
      setSelectedCategory((prev) => (prev > 0 ? prev - 1 : settings.length - 1));
      setSelectedItem(0);
    } else if (key.rightArrow) {
      // 右箭头：选择下一分类
      setSelectedCategory((prev) => (prev < settings.length - 1 ? prev + 1 : 0));
      setSelectedItem(0);
    } else if (key.return) {
      // 回车：开始编辑或切换布尔值
      if (currentItem) {
        if (currentItem.type === "boolean") {
          // 布尔类型直接切换
          handleToggle(currentItem.key);
        } else if (currentItem.type === "select") {
          // 选择类型切换到下一选项
          handleSelectNext(currentItem.key);
        } else {
          // 文本/数字类型进入编辑模式
          setIsEditing(true);
          setEditBuffer(String(currentItem.value));
        }
      }
    } else if (key.tab) {
      // Tab：保存设置
      handleSave();
    }
  });

  /**
   * 处理布尔值切换
   */
  const handleToggle = useCallback((key: string) => {
    setSettings((prev) =>
      prev.map((cat) => ({
        ...cat,
        items: cat.items.map((item) =>
          item.key === key ? { ...item, value: !item.value } : item
        ),
      }))
    );
    setHasChanges(true);
  }, []);

  /**
   * 处理选择类型切换到下一选项
   */
  const handleSelectNext = useCallback((key: string) => {
    setSettings((prev) =>
      prev.map((cat) => ({
        ...cat,
        items: cat.items.map((item) => {
          if (item.key === key && item.options) {
            const currentIndex = item.options.indexOf(item.value);
            const nextIndex = (currentIndex + 1) % item.options.length;
            return { ...item, value: item.options[nextIndex] };
          }
          return item;
        }),
      }))
    );
    setHasChanges(true);
  }, []);

  /**
   * 处理编辑确认
   */
  const handleEditConfirm = useCallback(() => {
    if (currentItem) {
      let newValue: any = editBuffer;

      // 类型转换
      if (currentItem.type === "number") {
        newValue = Number(editBuffer);
        if (isNaN(newValue)) {
          newValue = currentItem.value;
        }
      }

      setSettings((prev) =>
        prev.map((cat) => ({
          ...cat,
          items: cat.items.map((item) =>
            item.key === currentItem.key ? { ...item, value: newValue } : item
          ),
        }))
      );
      setHasChanges(true);
    }

    setIsEditing(false);
    setEditBuffer("");
  }, [currentItem, editBuffer]);

  /**
   * 处理保存
   */
  const handleSave = useCallback(() => {
    const settingsMap: Record<string, any> = {};
    settings.forEach((cat) => {
      cat.items.forEach((item) => {
        settingsMap[item.key] = item.value;
      });
    });

    onSave?.(settingsMap);
    setHasChanges(false);
  }, [settings, onSave]);

  /**
   * 渲染设置项值
   */
  const renderItemValue = (item: SettingsItem) => {
    if (isEditing && currentItem?.key === item.key) {
      // 编辑模式：显示输入缓冲区
      return (
        <Text color="yellow">
          {editBuffer}
          <Text color="gray">{"█"}</Text>
        </Text>
      );
    }

    // 根据类型显示值
    switch (item.type) {
      case "boolean":
        return (
          <Text color={item.value ? "green" : "red"}>
            {item.value ? "✓ 开启" : "✗ 关闭"}
          </Text>
        );
      case "select":
        return (
          <Text color="cyan">
            {item.value}
            <Text color="gray"> {"◀ ▶"}</Text>
          </Text>
        );
      default:
        return <Text color="white">{String(item.value) || "(空)"}</Text>;
    }
  };

  return (
    <Box flexDirection="column" height="100%">
      {/* 标题栏 */}
      <Box paddingX={1} paddingY={0}>
        <Text color={COLORS.primary} bold>
          {ICONS.settings} 设置
        </Text>
        {hasChanges && (
          <Text color="yellow"> (有未保存的更改)</Text>
        )}
      </Box>

      {/* 分隔线 */}
      <Box>
        <Text color="gray">{"─".repeat(60)}</Text>
      </Box>

      {/* 主内容区域：分类列表 + 设置项列表 */}
      <Box flexDirection="row" flexGrow={1}>
        {/* 左侧：分类列表 */}
        <Box
          flexDirection="column"
          width={20}
          borderStyle="single"
          borderColor="gray"
          paddingX={1}
        >
          {settings.map((cat, i) => (
            <Box key={cat.name}>
              <Text
                color={i === selectedCategory ? COLORS.primary : "white"}
                bold={i === selectedCategory}
              >
                {i === selectedCategory ? "▶ " : "  "}
                {cat.name}
              </Text>
            </Box>
          ))}
        </Box>

        {/* 右侧：设置项列表 */}
        <Box flexDirection="column" flexGrow={1} paddingX={1}>
          {/* 当前分类标题 */}
          <Box marginBottom={1}>
            <Text color={COLORS.primary} bold>
              {settings[selectedCategory]?.name}
            </Text>
          </Box>

          {/* 设置项列表 */}
          {currentItems.map((item, i) => (
            <Box key={item.key} flexDirection="column">
              <Box>
                {/* 选中指示器 */}
                <Text color={i === selectedItem ? COLORS.primary : "gray"}>
                  {i === selectedItem ? "● " : "○ "}
                </Text>

                {/* 设置项标签 */}
                <Text
                  color={i === selectedItem ? "white" : "gray"}
                  bold={i === selectedItem}
                >
                  {item.label}
                  {": "}
                </Text>

                {/* 设置项值 */}
                {renderItemValue(item)}
              </Box>

              {/* 设置项描述（仅选中时显示） */}
              {i === selectedItem && item.description && (
                <Box paddingLeft={2}>
                  <Text color="gray" italic>
                    {item.description}
                  </Text>
                </Box>
              )}
            </Box>
          ))}
        </Box>
      </Box>

      {/* 底部状态栏 */}
      <Box paddingX={1}>
        <Text color="gray">
          ↑↓ 选择 | ←→ 切换分类 | Enter 编辑/切换 | Tab 保存 | Esc 退出
        </Text>
      </Box>
    </Box>
  );
}

// 导出Settings组件作为默认导出
export default Settings;