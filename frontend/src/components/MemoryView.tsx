import React, { useState, useEffect } from "react";
import { Box, Text } from "ink";
import { api } from "../services/api";

interface MemoryViewProps {
  project: string;
  layer: string;
}

const LAYER_LABELS: Record<string, string> = {
  global: "全局",
  project: "项目",
  task: "任务",
  session: "会话",
  checkpoint: "快照",
  notes: "备忘",
};

const LAYER_COLORS: Record<string, string> = {
  global: "cyan",
  project: "blue",
  task: "green",
  session: "yellow",
  checkpoint: "magenta",
  notes: "gray",
};

export function MemoryView({ project, layer }: MemoryViewProps) {
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const loadMemory = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.getMemory(project, layer);
        if (!cancelled) {
          setContent(response.data.content);
        }
      } catch {
        if (!cancelled) {
          setError("加载失败");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadMemory();
    return () => { cancelled = true; };
  }, [project, layer]);

  const label = LAYER_LABELS[layer] || layer;
  const color = LAYER_COLORS[layer] || "white";

  if (loading) {
    return <Text color="gray">加载 {label} Memory 中...</Text>;
  }

  if (error) {
    return <Text color="red">{error}</Text>;
  }

  return (
    <Box flexDirection="column" borderStyle="single" padding={1}>
      <Text color={color} bold>[{label} Memory]</Text>
      <Box marginTop={1}>
        <Text>{content || "（空）"}</Text>
      </Box>
    </Box>
  );
}

export default MemoryView;
