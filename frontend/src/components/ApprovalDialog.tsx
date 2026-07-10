import React from "react";
import { Box, Text, useInput } from "ink";

interface ApprovalDialogProps {
  plan: string;
  agent: string;
  reason: string;
  onApprove: () => void;
  onReject: () => void;
}

const AGENT_LABELS: Record<string, string> = {
  "simple-coder": "简单编码",
  "complex-coder": "复杂编码",
  tester: "测试验证",
};

export function ApprovalDialog({
  plan,
  agent,
  reason,
  onApprove,
  onReject,
}: ApprovalDialogProps) {
  useInput((input, key) => {
    if (input === "y" || input === "Y") {
      onApprove();
    } else if (input === "n" || input === "N") {
      onReject();
    }
  });

  const label = AGENT_LABELS[agent] || agent;

  return (
    <Box flexDirection="column" borderStyle="double" padding={1}>
      <Text color="yellow" bold>[审批] 需要确认</Text>
      <Box marginTop={1}>
        <Text>即将委派 </Text>
        <Text color="cyan" bold>{label}</Text>
        <Text> 执行任务</Text>
      </Box>
      <Box marginTop={1}>
        <Text color="gray">原因: {reason}</Text>
      </Box>
      <Box marginTop={1}>
        <Text color="gray">计划: {plan}</Text>
      </Box>
      <Box marginTop={1}>
        <Text color="green">[Y] 确认 </Text>
        <Text color="red">[N] 取消</Text>
      </Box>
    </Box>
  );
}

export default ApprovalDialog;
