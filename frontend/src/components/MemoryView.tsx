// 导入 React 库和 Hooks
import React, { useState, useEffect } from "react";
// 导入 Ink 组件
import { Box, Text } from "ink";
// 导入 API 客户端
import { api } from "../services/api";

/**
 * Memory 浏览组件属性接口
 */
interface MemoryViewProps {
  project: string;  // 项目名称
  layer: string;    // Memory 层级（global/project/task/session/checkpoint/notes）
}

/**
 * Memory 层级中文标签映射
 * 将英文层级名称转换为中文显示
 */
const LAYER_LABELS: Record<string, string> = {
  global: "全局",        // 全局 Memory：编码偏好、通用规范
  project: "项目",       // 项目 Memory：架构决策、模块说明
  task: "任务",          // 任务 Memory：单任务目标、进展
  session: "会话",       // 会话 Memory：对话历史摘要
  checkpoint: "快照",    // 检查点：文件变更列表、快照摘要
  notes: "备忘",         // 备忘：TODO、临时记录
};

/**
 * Memory 层级颜色映射
 * 不同层级使用不同颜色显示
 */
const LAYER_COLORS: Record<string, string> = {
  global: "cyan",        // 全局：青色
  project: "blue",       // 项目：蓝色
  task: "green",         // 任务：绿色
  session: "yellow",     // 会话：黄色
  checkpoint: "magenta", // 快照：品红色
  notes: "gray",         // 备忘：灰色
};

/**
 * Memory 浏览组件
 * 从后端加载并显示指定层级的 Memory 内容
 *
 * @param project - 项目名称
 * @param layer - Memory 层级
 */
export function MemoryView({ project, layer }: MemoryViewProps) {
  // 状态定义
  const [content, setContent] = useState<string>("");      // Memory 内容
  const [loading, setLoading] = useState(true);             // 加载状态
  const [error, setError] = useState<string | null>(null);  // 错误信息

  // 组件挂载或参数变化时加载 Memory
  useEffect(() => {
    let cancelled = false;  // 取消标记，防止组件卸载后更新状态

    const loadMemory = async () => {
      setLoading(true);    // 开始加载
      setError(null);      // 清除错误
      try {
        // 调用 API 获取 Memory 内容
        const response = await api.getMemory(project, layer);
        if (!cancelled) {
          setContent(response.data.content);  // 设置内容
        }
      } catch {
        if (!cancelled) {
          setError("加载失败");  // 设置错误
        }
      } finally {
        if (!cancelled) {
          setLoading(false);  // 结束加载
        }
      }
    };

    loadMemory();
    // 清理函数：组件卸载时取消请求
    return () => { cancelled = true; };
  }, [project, layer]);  // 依赖项：project 和 layer 变化时重新加载

  // 获取中文标签和颜色
  const label = LAYER_LABELS[layer] || layer;
  const color = LAYER_COLORS[layer] || "white";

  // 加载中状态
  if (loading) {
    return <Text color="gray">加载 {label} Memory 中...</Text>;
  }

  // 错误状态
  if (error) {
    return <Text color="red">{error}</Text>;
  }

  // 正常显示
  return (
    <Box flexDirection="column" borderStyle="single" padding={1}>
      {/* 标题：层级名称 */}
      <Text color={color} bold>[{label} Memory]</Text>
      {/* 内容区域 */}
      <Box marginTop={1}>
        <Text>{content || "（空）"}</Text>
      </Box>
    </Box>
  );
}

// 默认导出
export default MemoryView;
