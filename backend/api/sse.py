"""
SSE (Server-Sent Events) 事件推送封装

本模块实现了 Server-Sent Events 的核心功能，包括：
1. SSE 事件类型定义（12种事件类型）
2. SSE 事件数据模型（Pydantic 模型）
3. SSE 事件对象封装
4. SSE 连接管理器（连接池、心跳、断线重连）
5. SSE 事件生成器（异步生成器）
6. 事件推送函数（便捷的事件推送接口）

SSE 是一种服务器向客户端推送数据的技术，
与 WebSocket 不同，SSE 是单向的（服务器→客户端），
适合用于实时状态更新、日志流等场景。
"""

# 导入必要的模块
import json  # JSON 序列化
import asyncio  # 异步编程
from typing import AsyncGenerator, Any, Optional, List, Dict  # 类型注解
from pydantic import BaseModel  # 数据验证模型
from dataclasses import dataclass, field  # 数据类
from datetime import datetime  # 时间处理


# ==================== SSE 事件类型定义 ====================
# 与前端 types/api.ts 中的 SSEEventType 保持一致
# 每种事件类型对应一种业务场景

class SSEEventType:
    """
    SSE 事件类型定义
    
    所有事件类型都是字符串常量，与前端的 TypeScript 类型定义保持一致
    这样可以确保前后端的事件类型完全匹配
    """
    
    # Agent 相关事件
    AGENT_START = "agent_start"  # Agent 开始执行
    CONSTRAINT_RESULT = "constraint_result"  # 约束检索结果
    
    # 工作流相关事件
    PLAN = "plan"  # Planner 输出计划
    APPROVAL_REQUIRED = "approval_required"  # 需要用户审批
    APPROVAL_RESPONSE = "approval_response"  # 用户审批响应
    
    # 工具和代码相关事件
    TOOL_CALL = "tool_call"  # Tool 调用
    CODE = "code"  # 代码生成
    
    # 测试和审查相关事件
    TEST_RESULT = "test_result"  # 测试结果
    REVIEW_RESULT = "review_result"  # 审查结果
    
    # 记忆和状态相关事件
    MEMORY_UPDATE = "memory_update"  # Memory 更新
    TEXT = "text"  # LLM 流式文本输出
    DONE = "done"  # 任务完成
    ERROR = "chat_error"  # 错误（避免与 SSE 内置 error 事件冲突）


# ==================== SSE 事件数据模型 ====================
# 使用 Pydantic 模型定义事件的数据结构
# 确保数据的类型安全和验证

class AgentStartEvent(BaseModel):
    """
    Agent 开始事件
    
    当一个 Agent 开始执行任务时触发
    用于前端显示当前正在运行的 Agent
    """
    agent: str  # Agent 名称，如 "planner", "complex_coder"
    status: str = "running"  # Agent 状态，默认为 "running"


class ConstraintResultEvent(BaseModel):
    """
    约束检索结果事件
    
    当 Constraint Agent 完成约束检索后触发
    返回检索到的相关约束列表和摘要
    """
    constraints: List[str]  # 检索到的约束列表
    summary: str  # 约束摘要


class PlanEvent(BaseModel):
    """
    计划事件
    
    当 Planner Agent 生成执行计划后触发
    包含任务列表和委派的 Agent
    """
    tasks: List[str]  # 任务列表
    delegated_agent: Optional[str] = None  # 委派的 Agent 名称


class ApprovalRequiredEvent(BaseModel):
    """
    需要审批事件
    
    当执行高风险操作时触发
    需要用户确认后才能继续执行
    """
    plan: str  # 执行计划
    agent: str  # 执行的 Agent
    reason: str  # 需要审批的原因


class ToolCallEvent(BaseModel):
    """
    Tool 调用事件
    
    当 Agent 调用工具时触发
    用于前端显示工具调用状态
    """
    tool: str  # 工具名称
    args: Dict[str, Any] = {}  # 工具参数


class CodeEvent(BaseModel):
    """
    代码生成事件
    
    当 Agent 生成代码后触发
    包含生成的文件路径和代码内容
    """
    file: str  # 文件路径
    content: str  # 代码内容


class TestResultEvent(BaseModel):
    """
    测试结果事件
    
    当 Tester Agent 完成测试后触发
    包含测试总数、通过数和错误信息
    """
    status: str  # 测试状态: "passed" 或 "failed"
    tests_total: int  # 测试总数
    tests_passed: int  # 通过的测试数
    errors: Optional[List[Dict]] = None  # 错误信息列表


class ReviewResultEvent(BaseModel):
    """
    审查结果事件
    
    当 Review Agent 完成审查后触发
    包含审查状态和违规信息
    """
    status: str  # 审查状态: "passed" 或 "failed"
    violations: List[Dict] = []  # 违规信息列表


class MemoryUpdateEvent(BaseModel):
    """
    Memory 更新事件
    
    当 Memory 系统更新后触发
    用于前端显示 Memory 更新状态
    """
    layers: List[str]  # 更新的 Memory 层
    message: str  # 更新消息


class TextEvent(BaseModel):
    """
    LLM 流式文本事件

    当 LLM 流式输出文本块时触发
    用于前端实时显示 AI 回复
    """
    content: str  # 文本内容
    agent: Optional[str] = None  # 处理消息的 Agent


class DoneEvent(BaseModel):
    """
    完成事件
    
    当整个任务完成后触发
    包含会话 ID 和任务摘要
    """
    session_id: str  # 会话 ID
    summary: str  # 任务摘要


class ErrorEvent(BaseModel):
    """
    错误事件
    
    当发生错误时触发
    包含错误信息
    """
    message: str  # 错误信息


# ==================== SSE 事件对象 ====================

class SSEEvent:
    """
    SSE 事件对象
    
    封装事件类型和数据，提供序列化方法
    用于在事件队列中传递
    """
    
    def __init__(self, event_type: str, data: Any):
        """
        初始化 SSE 事件
        
        Args:
            event_type: 事件类型（来自 SSEEventType）
            data: 事件数据（通常是 Pydantic 模型的字典形式）
        """
        self.event_type = event_type  # 事件类型
        self.data = data  # 事件数据
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            包含 type 和 data 的字典
        """
        return {"type": self.event_type, "data": self.data}
    
    def to_json(self) -> str:
        """
        转换为 JSON 字符串
        
        Returns:
            JSON 格式的字符串，ensure_ascii=False 支持中文
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)


# ==================== SSE 连接管理 ====================

@dataclass
class SSEConnection:
    """
    SSE 连接数据类
    
    存储单个 SSE 连接的状态信息
    用于连接管理和心跳检测
    """
    connection_id: str  # 连接唯一标识
    session_id: str  # 会话 ID
    queue: asyncio.Queue  # 事件队列
    created_at: datetime = field(default_factory=datetime.now)  # 创建时间
    last_heartbeat: datetime = field(default_factory=datetime.now)  # 最后心跳时间
    is_active: bool = True  # 连接是否活跃


class ConnectionManager:
    """
    SSE 连接管理器
    
    管理所有 SSE 连接的生命周期，提供：
    - 连接创建和销毁
    - 连接查询
    - 心跳检测
    - 活跃连接统计
    """
    
    def __init__(self):
        """初始化连接管理器"""
        # 使用字典存储所有连接，key 为 connection_id
        self.connections: Dict[str, SSEConnection] = {}
    
    def create_connection(self, session_id: str) -> SSEConnection:
        """
        创建新的 SSE 连接
        
        Args:
            session_id: 会话 ID
        
        Returns:
            新创建的 SSEConnection 对象
        """
        # 生成唯一的连接 ID
        connection_id = f"conn_{session_id}_{datetime.now().timestamp()}"
        # 创建事件队列
        queue: asyncio.Queue = asyncio.Queue()
        # 创建连接对象
        connection = SSEConnection(
            connection_id=connection_id,
            session_id=session_id,
            queue=queue,
        )
        # 存储到连接池
        self.connections[connection_id] = connection
        return connection
    
    def get_connection(self, connection_id: str) -> Optional[SSEConnection]:
        """
        根据连接 ID 获取连接
        
        Args:
            connection_id: 连接 ID
        
        Returns:
            SSEConnection 对象，如果不存在返回 None
        """
        return self.connections.get(connection_id)
    
    def remove_connection(self, connection_id: str) -> None:
        """
        移除连接
        
        Args:
            connection_id: 要移除的连接 ID
        """
        if connection_id in self.connections:
            # 先标记为非活跃
            self.connections[connection_id].is_active = False
            # 然后从字典中删除
            del self.connections[connection_id]
    
    def get_active_connections(self) -> List[SSEConnection]:
        """
        获取所有活跃连接
        
        Returns:
            活跃连接列表
        """
        # 过滤出所有活跃的连接
        return [conn for conn in self.connections.values() if conn.is_active]
    
    async def heartbeat(self, connection_id: str) -> None:
        """
        更新连接的心跳时间
        
        Args:
            connection_id: 连接 ID
        """
        conn = self.get_connection(connection_id)
        if conn:
            # 更新最后心跳时间
            conn.last_heartbeat = datetime.now()


# 创建全局连接管理器实例
connection_manager = ConnectionManager()


# ==================== SSE 事件生成器 ====================

async def sse_generator(event_queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """
    SSE 事件生成器
    
    这是一个异步生成器，从事件队列中读取事件，
    并生成符合 SSE 格式的字符串。
    
    SSE 格式：
    ```
    event: <事件类型>
    data: <JSON 数据>
    
    ```
    
    Args:
        event_queue: 事件队列
    
    Yields:
        SSE 格式的字符串
    """
    while True:
        # 从队列中获取事件
        event = await event_queue.get()
        # 如果收到 None，表示结束
        if event is None:
            break
        # 生成 SSE 格式的字符串
        yield f"event: {event.event_type}\ndata: {json.dumps(event.data, ensure_ascii=False)}\n\n"


# ==================== 事件推送函数 ====================
# 这些函数提供了便捷的事件推送接口
# 每个函数对应一种事件类型

async def push_event(
    event_queue: asyncio.Queue, event_type: str, data: Any
) -> None:
    """
    推送通用事件到队列
    
    Args:
        event_queue: 事件队列
        event_type: 事件类型
        data: 事件数据
    """
    # 创建 SSE 事件对象
    event = SSEEvent(event_type, data)
    # 将事件放入队列
    await event_queue.put(event)


async def push_agent_start(
    event_queue: asyncio.Queue, agent: str, status: str = "running"
) -> None:
    """
    推送 Agent 开始事件
    
    Args:
        event_queue: 事件队列
        agent: Agent 名称
        status: Agent 状态
    """
    # 创建事件数据
    data = AgentStartEvent(agent=agent, status=status).model_dump()
    # 推送事件
    await push_event(event_queue, SSEEventType.AGENT_START, data)


async def push_constraint_result(
    event_queue: asyncio.Queue, constraints: List[str], summary: str
) -> None:
    """
    推送约束检索结果事件
    
    Args:
        event_queue: 事件队列
        constraints: 约束列表
        summary: 约束摘要
    """
    data = ConstraintResultEvent(constraints=constraints, summary=summary).model_dump()
    await push_event(event_queue, SSEEventType.CONSTRAINT_RESULT, data)


async def push_plan(
    event_queue: asyncio.Queue, tasks: List[str], delegated_agent: Optional[str] = None
) -> None:
    """
    推送计划事件
    
    Args:
        event_queue: 事件队列
        tasks: 任务列表
        delegated_agent: 委派的 Agent
    """
    data = PlanEvent(tasks=tasks, delegated_agent=delegated_agent).model_dump()
    await push_event(event_queue, SSEEventType.PLAN, data)


async def push_approval_required(
    event_queue: asyncio.Queue, plan: str, agent: str, reason: str
) -> None:
    """
    推送需要审批事件
    
    Args:
        event_queue: 事件队列
        plan: 执行计划
        agent: 执行的 Agent
        reason: 需要审批的原因
    """
    data = ApprovalRequiredEvent(plan=plan, agent=agent, reason=reason).model_dump()
    await push_event(event_queue, SSEEventType.APPROVAL_REQUIRED, data)


async def push_tool_call(
    event_queue: asyncio.Queue, tool: str, args: Dict[str, Any] = {}
) -> None:
    """
    推送 Tool 调用事件
    
    Args:
        event_queue: 事件队列
        tool: 工具名称
        args: 工具参数
    """
    data = ToolCallEvent(tool=tool, args=args).model_dump()
    await push_event(event_queue, SSEEventType.TOOL_CALL, data)


async def push_code(
    event_queue: asyncio.Queue, file: str, content: str
) -> None:
    """
    推送代码生成事件
    
    Args:
        event_queue: 事件队列
        file: 文件路径
        content: 代码内容
    """
    data = CodeEvent(file=file, content=content).model_dump()
    await push_event(event_queue, SSEEventType.CODE, data)


async def push_test_result(
    event_queue: asyncio.Queue,
    status: str,
    tests_total: int,
    tests_passed: int,
    errors: Optional[List[Dict]] = None,
) -> None:
    """
    推送测试结果事件
    
    Args:
        event_queue: 事件队列
        status: 测试状态
        tests_total: 测试总数
        tests_passed: 通过的测试数
        errors: 错误信息列表
    """
    data = TestResultEvent(
        status=status, tests_total=tests_total, tests_passed=tests_passed, errors=errors
    ).model_dump()
    await push_event(event_queue, SSEEventType.TEST_RESULT, data)


async def push_review_result(
    event_queue: asyncio.Queue, status: str, violations: List[Dict] = []
) -> None:
    """
    推送审查结果事件
    
    Args:
        event_queue: 事件队列
        status: 审查状态
        violations: 违规信息列表
    """
    data = ReviewResultEvent(status=status, violations=violations).model_dump()
    await push_event(event_queue, SSEEventType.REVIEW_RESULT, data)


async def push_memory_update(
    event_queue: asyncio.Queue, layers: List[str], message: str
) -> None:
    """
    推送 Memory 更新事件
    
    Args:
        event_queue: 事件队列
        layers: 更新的 Memory 层
        message: 更新消息
    """
    data = MemoryUpdateEvent(layers=layers, message=message).model_dump()
    await push_event(event_queue, SSEEventType.MEMORY_UPDATE, data)


async def push_text(event_queue: asyncio.Queue, content: str, agent: Optional[str] = None) -> None:
    """
    推送 LLM 流式文本事件

    Args:
        event_queue: 事件队列
        content: 文本内容
        agent: 处理消息的 Agent
    """
    data = TextEvent(content=content, agent=agent).model_dump()
    await push_event(event_queue, SSEEventType.TEXT, data)


async def push_done(event_queue: asyncio.Queue, session_id: str, summary: str) -> None:
    """
    推送完成事件
    
    Args:
        event_queue: 事件队列
        session_id: 会话 ID
        summary: 任务摘要
    """
    data = DoneEvent(session_id=session_id, summary=summary).model_dump()
    await push_event(event_queue, SSEEventType.DONE, data)
    # 放入 None 作为结束信号
    await event_queue.put(None)


async def push_error(event_queue: asyncio.Queue, message: str) -> None:
    """
    推送错误事件
    
    Args:
        event_queue: 事件队列
        message: 错误信息
    """
    data = ErrorEvent(message=message).model_dump()
    await push_event(event_queue, SSEEventType.ERROR, data)
    # 放入 None 作为结束信号
    await event_queue.put(None)
