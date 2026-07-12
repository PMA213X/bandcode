"""
SimpleCoder Agent - 简单编码智能体

本模块实现了简单编码智能体，负责：
1. UI修改：样式调整、布局优化、文本修改
2. 配置调整：配置文件参数修改
3. 单文件修改：单个文件内的代码变更
4. 小型Bug修复：简单的逻辑修复、拼写错误等

作者：成员C（wang123456-123456）
"""

# 导入JSON解析
import json
# 导入正则表达式
import re
# 导入类型提示
from typing import Optional

# 导入Agent基类
from agents.base import BaseAgent, PipelineState
# 导入LLM客户端
from models.llm import LLMClient


class SimpleCoderAgent(BaseAgent):
    """
    简单编码智能体

    负责简单的编码任务，如UI修改、配置调整、单文件修改等。
    """

    # Agent名称
    name = "simple-coder"
    # Agent描述
    description = "简单编码智能体"
    # 使用的模型
    model = "mimo-v2.5"
    # 生成温度
    temperature = 0.2
    # 工具权限
    permissions = {
        "read": "allow",
        "edit": "allow",
        "bash": "allow"
    }

    def __init__(self, llm_client: LLMClient):
        """
        初始化SimpleCoder Agent

        Args:
            llm_client: LLM客户端实例
        """
        # 调用父类初始化
        super().__init__(llm_client)
        # 自动升级阈值
        self.max_files = 2
        self.max_lines = 300

    async def run(self, state: PipelineState) -> PipelineState:
        """
        执行简单编码任务

        Args:
            state: 当前工作流状态

        Returns:
            修改后的工作流状态
        """
        # 上报状态：开始执行
        self.report_status("running", {"step": "分析任务"})

        try:
            # 1. 分析任务
            task_analysis = await self._analyze_task(state)
            self.logger.info(f"任务分析完成: {task_analysis.get('type', 'N/A')}")

            # 2. 检查是否需要升级
            if self._should_upgrade(task_analysis):
                # 升级到ComplexCoder
                state.plan["delegated_agent"] = "complex-coder"
                state.plan["reason"] = "任务复杂度超出SimpleCoder处理能力"
                self.logger.info("任务升级到ComplexCoder")
                self.report_status("upgraded", {"reason": "任务升级"})
                return state

            # 3. 生成代码
            code = await self._generate_code(task_analysis, state)
            self.logger.info(f"代码生成完成, 长度: {len(code)}")

            # 4. 应用代码变更
            changes = await self._apply_changes(code, state)

            # 更新状态
            state.code = code
            state.files_changed = changes

            # 记录到历史
            self.add_to_history(state, "coding", {"files": len(changes)})

            # 上报状态：完成
            self.report_status("completed", {"changes": changes})

            return state

        except Exception as e:
            # 上报错误
            self.logger.error(f"编码任务失败: {e}")
            state.error = str(e)
            self.report_status("failed", {"error": str(e)})
            return state

    def _extract_json(self, text: str) -> dict:
        """
        从LLM响应中提取JSON

        Args:
            text: LLM响应文本

        Returns:
            解析后的JSON字典
        """
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取```json ... ```格式
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试提取{ ... }格式
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # 解析失败返回默认值
        return {}

    async def _analyze_task(self, state: PipelineState) -> dict:
        """
        分析任务

        Args:
            state: 当前工作流状态

        Returns:
            任务分析结果
        """
        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个任务分析器。请分析编码任务，确定：
1. 需要修改的文件
2. 修改的类型（UI/配置/逻辑）
3. 预估代码行数

输出格式（JSON）：
{
    "files": ["文件路径列表"],
    "type": "ui|config|logic",
    "estimated_lines": 100,
    "complexity": "low|medium|high"
}"""
            },
            {
                "role": "user",
                "content": f"""任务描述：
{state.user_input}

计划：
{json.dumps(state.plan, ensure_ascii=False, indent=2) if state.plan else "无"}

请分析任务："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0.2)

        # 解析响应
        analysis = self._extract_json(response)

        # 设置默认值
        if not analysis:
            analysis = {
                "files": [],
                "type": "logic",
                "estimated_lines": 100,
                "complexity": "low"
            }

        return analysis

    async def _generate_code(self, analysis: dict, state: PipelineState) -> str:
        """
        生成代码

        Args:
            analysis: 任务分析结果
            state: 当前工作流状态

        Returns:
            生成的代码
        """
        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个代码生成器。请根据任务分析生成代码。

要求：
1. 输出完整代码
2. 遵循项目约束
3. 代码简洁清晰
4. 添加必要的注释"""
            },
            {
                "role": "user",
                "content": f"""任务分析：
{json.dumps(analysis, ensure_ascii=False, indent=2)}

约束：
{state.constraint_summary}

请生成代码："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0.2)
        return response

    def _should_upgrade(self, analysis: dict) -> bool:
        """
        检查是否需要升级到ComplexCoder

        Args:
            analysis: 任务分析结果

        Returns:
            是否需要升级
        """
        # 检查文件数量
        if len(analysis.get("files", [])) > self.max_files:
            return True

        # 检查代码行数
        if analysis.get("estimated_lines", 0) > self.max_lines:
            return True

        # 检查复杂度
        if analysis.get("complexity") == "high":
            return True

        return False

    async def _apply_changes(self, code: str, state: PipelineState) -> list[dict]:
        """
        应用代码变更

        Args:
            code: 生成的代码
            state: 当前工作流状态

        Returns:
            变更文件列表
        """
        # 这里应该调用Tool来应用变更
        # 简化处理：返回空列表
        changes = []

        # 记录变更
        self.add_to_history(state, "apply_changes", {"code_length": len(code)})

        return changes
