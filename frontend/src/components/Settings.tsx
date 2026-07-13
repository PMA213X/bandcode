/**
 * Settings.tsx - 设置面板组件
 * 功能：全中文6大类设置展示与修改，连接后端 API
 */

import React, { useState, useCallback } from "react";
import { Box, Text, useInput, useApp } from "ink";
import { COLORS, ICONS } from "../styles/colors";
import { useSettings } from "../hooks/useSettings";
import { api } from "../services/api";
import ModelSelector from "./ModelSelector";
import { ModelProvider } from "../utils/modelProviders";

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
      { key: "默认模型", label: "默认模型", type: "text", description: "默认使用的LLM模型" },
      { key: "Base URL", label: "Base URL", type: "text", description: "LLM API基础地址" },
      { key: "API Key", label: "API Key", type: "text", description: "LLM API密钥" },
      { key: "Planner 模型", label: "Planner 模型", type: "text", description: "规划调度Agent使用的模型" },
      { key: "SimpleCoder 模型", label: "SimpleCoder 模型", type: "text", description: "SimpleCoder使用的模型" },
      { key: "ComplexCoder 模型", label: "ComplexCoder 模型", type: "text", description: "ComplexCoder使用的模型" },
      { key: "Tester 模型", label: "Tester 模型", type: "text", description: "Tester使用的模型" },
    ],
  },
  "Agent 设置": {
    icon: "🧑‍💻",
    items: [
      { key: "默认Agent", label: "默认Agent", type: "select", options: ["planner", "simple-coder", "complex-coder"], description: "默认使用的Agent" },
      { key: "审批模式", label: "审批模式", type: "boolean", description: "高风险操作是否需要用户确认" },
    ],
  },
  "Memory 设置": {
    icon: "🧠",
    items: [
      { key: "自动更新Memory", label: "自动更新Memory", type: "boolean", description: "是否自动更新Memory" },
      { key: "Memory压缩", label: "Memory压缩", type: "boolean", description: "是否启用Memory压缩" },
      { key: "压缩阈值", label: "压缩阈值", type: "number", description: "Memory条目数超过此值时压缩" },
    ],
  },
  "Workflow 设置": {
    icon: "⚡",
    items: [
      { key: "开启约束智能检索", label: "开启约束智能检索", type: "boolean", description: "是否启用Constraint Agent" },
      { key: "开启自动约束检查", label: "开启自动约束检查", type: "boolean", description: "是否启用Review Agent" },
      { key: "自动修正", label: "自动修正", type: "boolean", description: "Review失败时是否自动修正" },
      { key: "最大修正次数", label: "最大修正次数", type: "number", description: "Review最大迭代次数" },
      { key: "修正失败自动回滚", label: "修正失败自动回滚", type: "boolean", description: "是否支持自动回滚" },
      { key: "自动更新文档", label: "自动更新文档", type: "boolean", description: "是否自动更新文档" },
      { key: "Git提交建议", label: "Git提交建议", type: "boolean", description: "是否启用Git提交建议" },
    ],
  },
  "RAG 设置": {
    icon: "📚",
    items: [
      { key: "知识库路径", label: "知识库路径", type: "text", description: "知识库文档目录" },
      { key: "检索数量", label: "检索数量", type: "number", description: "每次检索返回的文档数量" },
      { key: "相似度阈值", label: "相似度阈值", type: "number", description: "相似度阈值（0-1）" },
    ],
  },
  "Tool 设置": {
    icon: "🔧",
    items: [
      { key: "工具目录", label: "工具目录", type: "text", description: "自定义工具目录" },
      { key: "自动发现", label: "自动发现", type: "boolean", description: "是否自动发现新工具" },
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
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  const { exit } = useApp();

  // 从后端数据构建分类列表，后端没有的字段使用默认值
  const settingsData = apiSettings as Record<string, Record<string, any>> | null;
  const categories: SettingsCategory[] = Object.entries(CATEGORY_META).map(([name, meta]) => ({
    name,
    items: meta.items.map((item) => ({
      ...item,
      value: settingsData?.[name]?.[item.key] ?? "",
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

  const handleTestModel = useCallback(async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const response = await api.testModel();
      if (response.code === 0 && response.data?.success) {
        setTestResult({
          success: true,
          message: `测试成功 (${response.data.latency}ms) - ${response.data.model}`,
        });
      } else {
        setTestResult({
          success: false,
          message: response.data?.error || response.message || "测试失败",
        });
      }
    } catch (err: any) {
      setTestResult({
        success: false,
        message: err.message || "测试请求失败",
      });
    } finally {
      setTesting(false);
    }
  }, []);

  useInput((inputChar, key) => {
    // Ctrl+C 退出
    if (key.ctrl && inputChar === "c") {
      exit();
      return;
    }

    // 模型选择器打开时，将所有输入交给 ModelSelector 处理
    if (showModelSelector) {
      return;
    }

    // Escape 键
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

    // 编辑模式下的输入处理
    if (isEditing) {
      if (key.return) {
        handleEditConfirm();
      } else if (key.backspace || key.delete) {
        setEditBuffer((prev) => prev.slice(0, -1));
      } else if (inputChar && !key.ctrl && !key.meta && !key.upArrow && !key.downArrow && !key.leftArrow && !key.rightArrow && !key.tab && !key.escape) {
        // 只有当 inputChar 非空且不是特殊键时才追加字符
        setEditBuffer((prev) => prev + inputChar);
      }
      return;
    }

    // 导航模式
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
        } else if (sectionName === "模型设置" && currentItem.key === "默认模型") {
          setShowModelSelector(true);
        } else {
          setIsEditing(true);
          setEditBuffer(String(currentItem.value));
        }
      }
    } else if (key.tab) {
      handleSave();
    } else if (inputChar === "r") {
      reloadSettings();
    } else if (inputChar === "p" && categories[selectedCategory]?.name === "模型设置") {
      setShowModelSelector(true);
    } else if (inputChar === "t" && categories[selectedCategory]?.name === "模型设置") {
      handleTestModel();
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
        {testing && <Text color="yellow"> (测试中...)</Text>}
        {testResult && (
          <Text color={testResult.success ? "green" : "red"}>
            {" "}{testResult.success ? "✓" : "✗"} {testResult.message}
          </Text>
        )}
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
          ↑↓ 选择 | ←→ 切换分类 | Enter 编辑/切换 | r 刷新 | p 选择提供商 | t 测试模型 | Esc 退出
        </Text>
      </Box>
      {showModelSelector && (
        <ModelSelector
          onSelectProvider={(provider) => {
            setSelectedProvider(provider);
            if (provider.baseUrl) {
              updateSetting("模型设置", "Base URL", provider.baseUrl);
            }
          }}
          onSelectModel={(model) => {
            updateSetting("模型设置", "默认模型", model.id);
          }}
          onClose={() => setShowModelSelector(false)}
          selectedProviderId={selectedProvider?.id}
        />
      )}
    </Box>
  );
}

export default Settings;
