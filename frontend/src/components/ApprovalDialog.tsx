// 导入 React 库
import React from "react";
// 导入 Ink 组件：Box 布局、Text 文本、useInput 键盘输入监听
import { Box, Text, useInput } from "ink";

/**
 * 审批弹窗组件属性接口
 */
interface ApprovalDialogProps {
  plan: string;          // 执行计划描述
  agent: string;         // 即将委派的 Agent 名称
  reason: string;        // 需要审批的原因
  onApprove: () => void; // 批准回调函数
  onReject: () => void;  // 拒绝回调函数
}

/**
 * Agent 中文标签映射
 * 用于显示即将执行任务的 Agent 名称
 */
const AGENT_LABELS: Record<string, string> = {
  "simple-coder": "简单编码",   // SimpleCoder Agent
  "complex-coder": "复杂编码",  // ComplexCoder Agent
  tester: "测试验证",           // Tester Agent
};

/**
 * 审批确认弹窗组件
 * 当 Planner 需要用户确认高风险操作时显示
 * 支持键盘 Y/N 快捷操作
 *
 * @param plan - 执行计划
 * @param agent - Agent 名称
 * @param reason - 审批原因
 * @param onApprove - 批准回调
 * @param onReject - 拒绝回调
 */
export function ApprovalDialog({
  plan,
  agent,
  reason,
  onApprove,
  onReject,
}: ApprovalDialogProps) {
  // 监听键盘输入
  useInput((input, key) => {
    if (input === "y" || input === "Y") {
      onApprove();  // 按 Y 批准
    } else if (input === "n" || input === "N") {
      onReject();   // 按 N 拒绝
    }
  });

  // 获取 Agent 中文标签
  const label = AGENT_LABELS[agent] || agent;

  return (
    <Box flexDirection="column" borderStyle="double" padding={1}>
      {/* 标题：审批提示 */}
      <Text color="yellow" bold>[审批] 需要确认</Text>

      {/* Agent 信息 */}
      <Box marginTop={1}>
        <Text>即将委派 </Text>
        <Text color="cyan" bold>{label}</Text>
        <Text> 执行任务</Text>
      </Box>

      {/* 审批原因 */}
      <Box marginTop={1}>
        <Text color="gray">原因: {reason}</Text>
      </Box>

      {/* 执行计划 */}
      <Box marginTop={1}>
        <Text color="gray">计划: {plan}</Text>
      </Box>

      {/* 操作按钮 */}
      <Box marginTop={1}>
        <Text color="green">[Y] 确认 </Text>
        <Text color="red">[N] 取消</Text>
      </Box>
    </Box>
  );
}

// 默认导出
export default ApprovalDialog;
