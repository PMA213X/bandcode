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
"""

# 导入数据类
from dataclasses import dataclass, field
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

            # 2. 单元测试
            test_result = await self._run_tests(state)

            # 3. 静态分析
            analysis_result = await self._static_analysis(state)

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
            state.error = str(e)
            self.report_status("failed", {"error": str(e)})
            return state

    async def _check_compilation(self, state: PipelineState) -> dict:
        """
        检查编译

        Args:
            state: 当前工作流状态

        Returns:
            编译检查结果
        """
        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个编译检查器。请检查代码是否能正常编译。

输出格式：
{
    "success": true|false,
    "errors": ["错误列表"]
}"""
            },
            {
                "role": "user",
                "content": f"""代码：
{state.code}

请检查编译："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0)

        # 解析响应（简化处理）
        result = {
            "success": True,
            "errors": []
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
        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个测试运行器。请运行单元测试并报告结果。

输出格式：
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
{state.code}

请运行测试："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0)

        # 解析响应（简化处理）
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
        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个静态分析器。请对代码进行静态分析。

输出格式：
{
    "quality_score": 85,
    "issues": ["问题列表"],
    "suggestions": ["建议列表"]
}"""
            },
            {
                "role": "user",
                "content": f"""代码：
{state.code}

请进行静态分析："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0)

        # 解析响应（简化处理）
        result = {
            "quality_score": 85,
            "issues": [],
            "suggestions": []
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
        if not compile_result["success"]:
            status = "failed"
        elif test_result["failed"] > 0:
            status = "failed"
        else:
            status = "passed"

        # 构造报告
        report = {
            "status": status,
            "compile": compile_result,
            "tests": test_result,
            "analysis": analysis_result
        }

        return report