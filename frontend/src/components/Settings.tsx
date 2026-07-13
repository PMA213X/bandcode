/**
 * Settings.tsx - 设置面板组件
 * 功能：全中文6大类设置展示与修改，连接后端 API
 */

import React, { useState, useCallback } from "react";
import { Box, Text, useInput, useApp } from "ink";
import { COLORS, ICONS } from "../styles/colors";
import { useSettings } from "../hooks/useSettings";
import ModelSelector from "./ModelSelector";
import { MODEL_PROVIDERS, ModelProvider, getProviderById } from "../utils/modelProviders";

interface SettingsCategory {
  name: string;
  items: SettingsItem[];
}

interface SettingsItem {
  key: string;
  label: string;
  type: "text" | "number" | "boolean" | "select";
  value: any;
  options?: string[];
  description?: string;
}

interface SettingsProps {
  onClose?: () => void;
  onSave?: (settings: Record<string, any>) => void;
}

const CATEGORY_META: Record<string, { icon: string; items: Omit<SettingsItem, "value">[] }> = {
  "模型设置": {
    icon: "🤖",
    items: [
      { key: "default_model", label: "默认模型", type: "text", description: "默认使用的LLM模型" },
      { key: "base_url", label: "Base URL", type: "text", description: "LLM API基础地址" },
      { key: "api_key", label: "API Key", type: "text", description: "LLM API密钥" },
      { key: "planner_model", label: "Planner 模型", type: "text", description: "规划调度Agent使用的模型" },
      { key: "temperature", label: "温度参数", type: "number", description: "LLM生成温度，0-1之间" },
      { key: "max_tokens", label: "最大Token数", type: "number", description: "单次生成最大Token数" },
      { key: "timeout", label: "超时时间(秒)", type: "number", description: "LLM请求超时时间" },
      { key: "max_retries", label: "最大重试次数", type: "number", description: "LLM请求失败重试次数" },
    ],
  },
  "Agent 设置": {
    icon: "🧑‍💻",
    items: [
      { key: "default_agent", label: "默认Agent", type: "select", options: ["planner", "simple-coder", "complex-coder"], description: "默认使用的Agent" },
      { key: "approval_mode", label: "审批模式", type: "boolean", description: "高风险操作是否需要用户确认" },
      { key: "max_iterations", label: "最大迭代次数", type: "number", description: "Agent最大迭代次数" },
      { key: "auto_retry", label: "自动重试", type: "boolean", description: "失败时是否自动重试" },
      { key: "verbose_logging", label: "详细日志", type: "boolean", description: "是否输出详细日志" },
      { key: "agent_timeout", label: "Agent超时(秒)", type: "number", description: "单个Agent执行超时时间" },
      { key: "parallel_agents", label: "并行Agent数", type: "number", description: "同时运行的Agent数量" },
    ],
  },
  "Memory 设置": {
    icon: "🧠",
    items: [
      { key: "auto_update_memory", label: "自动更新Memory", type: "boolean", description: "是否自动更新Memory" },
      { key: "memory_compression", label: "Memory压缩", type: "boolean", description: "是否启用Memory压缩" },
      { key: "compression_threshold", label: "压缩阈值", type: "number", description: "Memory条目数超过此值时压缩" },
      { key: "global_memory_path", label: "Global Memory路径", type: "text", description: "全局Memory存储路径" },
      { key: "project_memory_path", label: "Project Memory路径", type: "text", description: "项目Memory存储路径" },
      { key: "task_memory_path", label: "Task Memory路径", type: "text", description: "任务Memory存储路径" },
      { key: "session_memory_path", label: "Session Memory路径", type: "text", description: "会话Memory存储路径" },
    ],
  },
  "Workflow 设置": {
    icon: "⚡",
    items: [
      { key: "enable_constraint_search", label: "开启约束智能检索", type: "boolean", description: "是否启用Constraint Agent" },
      { key: "enable_auto_review", label: "开启自动约束检查", type: "boolean", description: "是否启用Review Agent" },
      { key: "auto_fix", label: "自动修正", type: "boolean", description: "Review失败时是否自动修正" },
      { key: "max_review_iterations", label: "最大Review次数", type: "number", description: "Review最大迭代次数" },
      { key: "enable_checkpoint", label: "开启快照管理", type: "boolean", description: "是否启用Checkpoint" },
      { key: "checkpoint_interval", label: "快照间隔(秒)", type: "number", description: "自动创建快照的间隔" },
      { key: "enable_rollback", label: "开启回滚功能", type: "boolean", description: "是否支持快照回滚" },
    ],
  },
  "RAG 设置": {
    icon: "📚",
    items: [
      { key: "knowledge_path", label: "知识库路径", type: "text", description: "知识库文档目录" },
      { key: "retrieval_count", label: "检索数量", type: "number", description: "每次检索返回的文档数量" },
      { key: "chunk_size", label: "分块大小", type: "number", description: "文档分块大小(字符)" },
      { key: "chunk_overlap", label: "分块重叠", type: "number", description: "分块重叠大小(字符)" },
      { key: "embedding_model", label: "Embedding模型", type: "text", description: "向量化使用的模型" },
      { key: "enable_rerank", label: "开启重排序", type: "boolean", description: "是否对检索结果重排序" },
    ],
  },
  "Tool 设置": {
    icon: "🔧",
    items: [
      { key: "tools_path", label: "工具目录", type: "text", description: "自定义工具目录" },
      { key: "enable_builtins", label: "启用内置工具", type: "boolean", description: "是否启用内置工具" },
      { key: "read_permission", label: "读取权限", type: "select", options: ["allow", "deny", "ask"], description: "文件读取权限" },
      { key: "write_permission", label: "写入权限", type: "select", options: ["allow", "deny", "ask"], description: "文件写入权限" },
      { key: "bash_permission", label: "Bash权限", type: "select", options: ["allow", "deny", "ask"], description: "Bash命令执行权限" },
      { key: "edit_permission", label: "编辑权限", type: "select", options: ["allow", "deny", "ask"], description: "文件编辑权限" },
      { key: "max_file_size", label: "最大文件大小(KB)", type: "number", description: "允许操作的最大文件大小" },
    ],
  },
};

export function Settings({ onClose, onSave }: SettingsProps) {
  const { settings: apiSettings, loading, error, saving, saveStatus, updateSetting, reloadSettings } = useSettings();

  const [selectedCategory, setSelectedCategory] = useState(0);
  const [selectedItem, setSelectedItem] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [editBuffer, setEditBuffer] = useState("");
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<ModelProvider | null>(null);

  const { exit } = useApp();

  // 从后端数据构建分类列表，后端没有的字段使用默认值
  const categories: SettingsCategory[] = Object.entries(CATEGORY_META).map(([name, meta]) => ({
    name,
    items: meta.items.map((item) => ({
      ...item,
      value: apiSettings?.[name]?.[item.key] ?? "",
    })),
  }));

  const currentItems = categories[selectedCategory]?.items || [];
  const currentItem = currentItems[selectedItem];

  const handleToggle = useCallback(async (section: string, key: string, currentValue: boolean) => {
    await updateSetting(section, key, !currentValue);
  }, [updateSetting]);

  const handleSelectNext = useCallback(async (section: string, key: string, currentValue: string, options: string[]) => {
    const currentIndex = options.indexOf(currentValue);
    const nextIndex = (currentIndex + 1) % options.length;
    await updateSetting(section, key, options[nextIndex]);
  }, [updateSetting]);

  const handleEditConfirm = useCallback(async () => {
    if (currentItem) {
      let newValue: any = editBuffer;
      if (currentItem.type === "number") {
        newValue = Number(editBuffer);
        if (isNaN(newValue)) newValue = currentItem.value;
      }
      const sectionName = categories[selectedCategory].name;
      await updateSetting(sectionName, currentItem.key, newValue);
    }
    setIsEditing(false);
    setEditBuffer("");
  }, [currentItem, editBuffer, selectedCategory, categories, updateSetting]);

  const handleSave = useCallback(() => {
    const settingsMap: Record<string, any> = {};
    categories.forEach((cat) => {
      cat.items.forEach((item) => {
        settingsMap[item.key] = item.value;
      });
    });
    onSave?.(settingsMap);
  }, [categories, onSave]);

  useInput((inputChar, key) => {
    if (key.ctrl && inputChar === "c") {
      exit();
      return;
    }

    if (key.escape) {
      if (isEditing) {
        setIsEditing(false);
        setEditBuffer("");
      } else if (onClose) {
        onClose();
      } else {
        exit();
      }
      return;
    }

    if (isEditing) {
      if (key.return) {
        handleEditConfirm();
      } else if (key.backspace) {
        setEditBuffer((prev) => prev.slice(0, -1));
      } else if (!key.ctrl && !key.meta) {
        setEditBuffer((prev) => prev + inputChar);
      }
      return;
    }

    if (key.upArrow) {
      setSelectedItem((prev) => (prev > 0 ? prev - 1 : currentItems.length - 1));
    } else if (key.downArrow) {
      setSelectedItem((prev) => (prev < currentItems.length - 1 ? prev + 1 : 0));
    } else if (key.leftArrow) {
      setSelectedCategory((prev) => (prev > 0 ? prev - 1 : categories.length - 1));
      setSelectedItem(0);
    } else if (key.rightArrow) {
      setSelectedCategory((prev) => (prev < categories.length - 1 ? prev + 1 : 0));
      setSelectedItem(0);
    } else if (key.return) {
      if (currentItem) {
        const sectionName = categories[selectedCategory].name;
        if (currentItem.type === "boolean") {
          handleToggle(sectionName, currentItem.key, currentItem.value);
        } else if (currentItem.type === "select" && currentItem.options) {
          handleSelectNext(sectionName, currentItem.key, currentItem.value, currentItem.options);
        } else if (sectionName === "模型设置" && currentItem.key === "default_model") {
          // 模型设置分类下选择默认模型时，打开模型选择器
          setShowModelSelector(true);
        } else {
          setIsEditing(true);
          setEditBuffer(String(currentItem.value));
        }
      }
    } else if (key.tab) {
      handleSave();
    } else if (inputChar === "r" && !isEditing) {
      reloadSettings();
    } else if (inputChar === "p" && !isEditing && categories[selectedCategory]?.name === "模型设置") {
      setShowModelSelector(true);
    }
  });

  const renderItemValue = (item: SettingsItem) => {
    if (isEditing && currentItem?.key === item.key) {
      return (
        <Text color="yellow">
          {editBuffer}
          <Text color="gray">{"█"}</Text>
        </Text>
      );
    }

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

  if (loading) {
    return (
      <Box padding={1}>
        <Text color={COLORS.info}>{ICONS.loading} 加载设置中...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box flexDirection="column" padding={1}>
        <Text color={COLORS.error}>{ICONS.error} {error}</Text>
        <Text color="gray">按 r 重试，Esc 退出</Text>
      </Box>
    );
  }

  const saveStatusText = saveStatus === "success" ? "✓ 已保存" : saveStatus === "error" ? "✗ 保存失败" : "";
  const saveStatusColor = saveStatus === "success" ? "green" : saveStatus === "error" ? "red" : "gray";

  return (
    <Box flexDirection="column" height="100%">
      <Box paddingX={1} paddingY={0}>
        <Text color={COLORS.primary} bold>
          {ICONS.settings} 设置
        </Text>
        {saving && <Text color="yellow"> (保存中...)</Text>}
        {saveStatusText && <Text color={saveStatusColor}> {saveStatusText}</Text>}
      </Box>
      <Box>
        <Text color="gray">{"─".repeat(60)}</Text>
      </Box>
      <Box flexDirection="row" flexGrow={1}>
        <Box
          flexDirection="column"
          width={20}
          borderStyle="single"
          borderColor="gray"
          paddingX={1}
        >
          {categories.map((cat, i) => (
            <Box key={cat.name}>
              <Text
                color={i === selectedCategory ? COLORS.primary : "white"}
                bold={i === selectedCategory}
              >
                {i === selectedCategory ? "▶ " : "  "}
                {CATEGORY_META[cat.name]?.icon} {cat.name}
              </Text>
            </Box>
          ))}
        </Box>
        <Box flexDirection="column" flexGrow={1} paddingX={1}>
          <Box marginBottom={1}>
            <Text color={COLORS.primary} bold>
              {categories[selectedCategory]?.name}
            </Text>
          </Box>
          {categories[selectedCategory]?.name === "模型设置" && (
            <Box flexDirection="column" marginBottom={1}>
              <Box>
                <Text color="yellow">模型提供商: </Text>
                <Text color="cyan" bold>
                  {selectedProvider
                    ? `${selectedProvider.icon} ${selectedProvider.name}`
                    : "按 p 选择提供商"}
                </Text>
              </Box>
              {selectedProvider && (
                <Box paddingLeft={2}>
                  <Text color="gray" italic>
                    选择提供商后自动填充 Base URL 和默认模型
                  </Text>
                </Box>
              )}
            </Box>
          )}
          {currentItems.map((item, i) => (
            <Box key={item.key} flexDirection="column">
              <Box>
                <Text color={i === selectedItem ? COLORS.primary : "gray"}>
                  {i === selectedItem ? "● " : "○ "}
                </Text>
                <Text
                  color={i === selectedItem ? "white" : "gray"}
                  bold={i === selectedItem}
                >
                  {item.label}
                  {": "}
                </Text>
                {renderItemValue(item)}
              </Box>
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
      <Box paddingX={1}>
        <Text color="gray">
          ↑↓ 选择 | ←→ 切换分类 | Enter 编辑/切换 | r 刷新 | p 选择提供商 | Esc 退出
        </Text>
      </Box>
      {showModelSelector && (
        <ModelSelector
          onSelectProvider={(provider) => {
            setSelectedProvider(provider);
            if (provider.baseUrl) {
              updateSetting("模型设置", "base_url", provider.baseUrl);
            }
          }}
          onSelectModel={(model) => {
            updateSetting("模型设置", "default_model", model.id);
          }}
          onClose={() => setShowModelSelector(false)}
          selectedProviderId={selectedProvider?.id}
        />
      )}
    </Box>
  );
}

export default Settings;
