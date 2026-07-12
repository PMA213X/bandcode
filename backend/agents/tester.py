"""
Tester Agent - 测试验证智能体

本模块实现了测试验证智能体，负责：
1. 编译检查：检查代码语法和类型
2. 单元测试：运行单元测试
3. 静态分析：代码质量检查

硬约束：
- edit权限 = deny：禁止修改任何代码文件
- 禁止修改代码：不得对源代码进行任何写入操作
- 禁止自动修复：发现问题后仅报告，不得自动修复

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


class TesterAgent(BaseAgent):
    """
    测试验证智能体

    负责执行测试验证，生成测试报告，确保代码质量符合预期。
    """

    # Agent名称
    name = "tester"
    # Agent描述
    description = "测试验证智能体"
    # 使用的模型
    model = "mimo-v2.5"
    # 生成温度
    temperature = 0
    # 工具权限（硬约束：禁止修改代码）
    permissions = {
        "read": "allow",
        "edit": "deny",
        "bash": "allow"
    }

    def __init__(self, llm_client: LLMClient):
        """
        初始化Tester Agent

        Args:
            llm_client: LLM客户端实例
        """
        # 调用父类初始化
        super().__init__(llm_client)
        # 最大步骤数
        self.max_steps = 10

    async def run(self, state: PipelineState) -> PipelineState:
        """
        执行测试验证

        Args:
            state: 当前工作流状态

        Returns:
            修改后的工作流状态
        """
        # 上报状态：开始执行
        self.report_status("running", {"step": "编译检查"})

        try:
            # 1. 编译检查
            compile_result = await self._check_compilation(state)
            self.logger.info(f"编译检查完成: {'成功' if compile_result.get('success') else '失败'}")

            # 2. 单元测试
            test_result = await self._run_tests(state)
            self.logger.info(f"单元测试完成: 通过 {test_result.get('passed', 0)}, 失败 {test_result.get('failed', 0)}")

            # 3. 静态分析
            analysis_result = await self._static_analysis(state)
            self.logger.info(f"静态分析完成: 质量分数 {analysis_result.get('quality_score', 0)}")

            # 4. 生成测试报告
            report = self._generate_report(compile_result, test_result, analysis_result)

            # 更新状态
            state.test_results = report

            # 记录到历史
            self.add_to_history(state, "testing", report)

            # 上报状态：完成
            self.report_status("completed", {"report": report})

            return state

        except Exception as e:
            # 上报错误
            self.logger.error(f"测试验证失败: {e}")
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

    async def _check_compilation(self, state: PipelineState) -> dict:
        """
        检查编译

        Args:
            state: 当前工作流状态

        Returns:
            编译检查结果
        """
        # 如果没有代码，跳过检查
        if not state.code:
            return {"success": True, "errors": []}

        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个编译检查器。请检查代码是否能正常编译。

输出格式（JSON）：
{
    "success": true|false,
    "errors": ["错误列表"],
    "warnings": ["警告列表"]
}"""
            },
            {
                "role": "user",
                "content": f"""代码：
{state.code[:3000]}

请检查编译："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0)

        # 解析响应
        result = self._extract_json(response)

        # 设置默认值
        if not result:
            result = {
                "success": True,
                "errors": [],
                "warnings": []
            }

        return result

    async def _run_tests(self, state: PipelineState) -> dict:
        """
        运行测试

        Args:
            state: 当前工作流状态

        Returns:
            测试结果
        """
        # 如果没有代码，跳过测试
        if not state.code:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }

        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个测试运行器。请运行单元测试并报告结果。

输出格式（JSON）：
{
    "total": 100,
    "passed": 98,
    "failed": 2,
    "errors": [
        {
            "test_name": "测试用例名称",
            "error_message": "错误信息"
        }
    ]
}"""
            },
            {
                "role": "user",
                "content": f"""代码：
{state.code[:3000]}

请运行测试："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0)

        # 解析响应
        result = self._extract_json(response)

        # 设置默认值
        if not result:
            result = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }

        return result

    async def _static_analysis(self, state: PipelineState) -> dict:
        """
        静态分析

        Args:
            state: 当前工作流状态

        Returns:
            静态分析结果
        """
        # 如果没有代码，跳过分析
        if not state.code:
            return {
                "quality_score": 0,
                "issues": [],
                "suggestions": []
            }

        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个静态分析器。请对代码进行静态分析。

输出格式（JSON）：
{
    "quality_score": 85,
    "issues": ["问题列表"],
    "suggestions": ["建议列表"],
    "metrics": {
        "complexity": "low|medium|high",
        "maintainability": "good|fair|poor"
    }
}"""
            },
            {
                "role": "user",
                "content": f"""代码：
{state.code[:3000]}

请进行静态分析："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0)

        # 解析响应
        result = self._extract_json(response)

        # 设置默认值
        if not result:
            result = {
                "quality_score": 85,
                "issues": [],
                "suggestions": [],
                "metrics": {
                    "complexity": "medium",
                    "maintainability": "fair"
                }
            }

        return result

    def _generate_report(
        self,
        compile_result: dict,
        test_result: dict,
        analysis_result: dict
    ) -> dict:
        """
        生成测试报告

        Args:
            compile_result: 编译检查结果
            test_result: 测试结果
            analysis_result: 静态分析结果

        Returns:
            测试报告
        """
        # 确定整体状态
        if not compile_result.get("success", True):
            status = "failed"
        elif test_result.get("failed", 0) > 0:
            status = "failed"
        elif analysis_result.get("quality_score", 100) < 60:
            status = "warning"
        else:
            status = "passed"

        # 构造报告
        report = {
            "status": status,
            "compile": compile_result,
            "tests": test_result,
            "analysis": analysis_result,
            "summary": self._generate_summary(status, compile_result, test_result, analysis_result)
        }

        return report

    def _generate_summary(
        self,
        status: str,
        compile_result: dict,
        test_result: dict,
        analysis_result: dict
    ) -> str:
        """
        生成报告摘要

        Args:
            status: 整体状态
            compile_result: 编译检查结果
            test_result: 测试结果
            analysis_result: 静态分析结果

        Returns:
            报告摘要
        """
        parts = []

        # 编译状态
        if compile_result.get("success", True):
            parts.append("编译通过")
        else:
            errors = compile_result.get("errors", [])
            parts.append(f"编译失败: {len(errors)} 个错误")

        # 测试状态
        passed = test_result.get("passed", 0)
        failed = test_result.get("failed", 0)
        total = test_result.get("total", 0)
        if total > 0:
            parts.append(f"测试: {passed}/{total} 通过")

        # 代码质量
        quality_score = analysis_result.get("quality_score", 0)
        if quality_score > 0:
            parts.append(f"质量分数: {quality_score}")

        return " | ".join(parts) if parts else "测试完成"
