"""
SSE (Server-Sent Events) 事件推送封装
定义事件类型、事件生成器、连接管理
"""
import json
import asyncio
from typing import AsyncGenerator, Any, Optional, List, Dict
from pydantic import BaseModel
from dataclasses import dataclass, field
from datetime import datetime


# ========== SSE 事件类型 ==========

class SSEEventType:
    """SSE 事件类型定义（与前端 types/api.ts 一致）"""

    AGENT_START = "agent_start"  # Agent 开始执行
    CONSTRAINT_RESULT = "constraint_result"  # 约束检索结果
    PLAN = "plan"  # Planner 输出计划
    APPROVAL_REQUIRED = "approval_required"  # 需要审批
    APPROVAL_RESPONSE = "approval_response"  # 审批响应
    TOOL_CALL = "tool_call"  # Tool 调用
    CODE = "code"  # 代码生成
    TEST_RESULT = "test_result"  # 测试结果
    REVIEW_RESULT = "review_result"  # 审查结果
    MEMORY_UPDATE = "memory_update"  # Memory 更新
    DONE = "done"  # 完成
    ERROR = "error"  # 错误


# ========== SSE 事件数据模型 ==========

class AgentStartEvent(BaseModel):
    """Agent 开始事件"""
    agent: str
    status: str = "running"


class ConstraintResultEvent(BaseModel):
    """约束检索结果事件"""
    constraints: List[str]
    summary: str


class PlanEvent(BaseModel):
    """计划事件"""
    tasks: List[str]
    delegated_agent: Optional[str] = None


class ApprovalRequiredEvent(BaseModel):
    """需要审批事件"""
    plan: str
    agent: str
    reason: str


class ToolCallEvent(BaseModel):
    """Tool 调用事件"""
    tool: str
    args: Dict[str, Any] = {}


class CodeEvent(BaseModel):
    """代码生成事件"""
    file: str
    content: str


class TestResultEvent(BaseModel):
    """测试结果事件"""
    status: str  # passed / failed
    tests_total: int
    tests_passed: int
    errors: Optional[List[Dict]] = None


class ReviewResultEvent(BaseModel):
    """审查结果事件"""
    status: str  # passed / failed
    violations: List[Dict] = []


class MemoryUpdateEvent(BaseModel):
    """Memory 更新事件"""
    layers: List[str]
    message: str


class DoneEvent(BaseModel):
    """完成事件"""
    session_id: str
    summary: str


class ErrorEvent(BaseModel):
    """错误事件"""
    message: str


# ========== SSE 事件对象 ==========

class SSEEvent:
    """SSE 事件对象"""

    def __init__(self, event_type: str, data: Any):
        self.event_type = event_type
        self.data = data

    def to_dict(self) -> dict:
        return {"type": self.event_type, "data": self.data}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


# ========== SSE 连接管理 ==========

@dataclass
class SSEConnection:
    """SSE 连接"""
    connection_id: str
    session_id: str
    queue: asyncio.Queue
    created_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    is_active: bool = True


class ConnectionManager:
    """SSE 连接管理器"""

    def __init__(self):
        self.connections: Dict[str, SSEConnection] = {}

    def create_connection(self, session_id: str) -> SSEConnection:
        """创建新连接"""
        connection_id = f"conn_{session_id}_{datetime.now().timestamp()}"
        queue: asyncio.Queue = asyncio.Queue()
        connection = SSEConnection(
            connection_id=connection_id,
            session_id=session_id,
            queue=queue,
        )
        self.connections[connection_id] = connection
        return connection

    def get_connection(self, connection_id: str) -> Optional[SSEConnection]:
        """获取连接"""
        return self.connections.get(connection_id)

    def remove_connection(self, connection_id: str) -> None:
        """移除连接"""
        if connection_id in self.connections:
            self.connections[connection_id].is_active = False
            del self.connections[connection_id]

    def get_active_connections(self) -> List[SSEConnection]:
        """获取所有活跃连接"""
        return [conn for conn in self.connections.values() if conn.is_active]

    async def heartbeat(self, connection_id: str) -> None:
        """更新心跳时间"""
        conn = self.get_connection(connection_id)
        if conn:
            conn.last_heartbeat = datetime.now()


# 全局连接管理器
connection_manager = ConnectionManager()


# ========== SSE 事件生成器 ==========

async def sse_generator(event_queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """
    SSE 事件生成器
    从队列中读取事件并生成 SSE 格式的响应
    """
    while True:
        event = await event_queue.get()
        if event is None:
            break
        yield f"event: {event.event_type}\ndata: {json.dumps(event.data, ensure_ascii=False)}\n\n"


# ========== 事件推送函数 ==========

async def push_event(
    event_queue: asyncio.Queue, event_type: str, data: Any
) -> None:
    """推送事件到队列"""
    event = SSEEvent(event_type, data)
    await event_queue.put(event)


async def push_agent_start(
    event_queue: asyncio.Queue, agent: str, status: str = "running"
) -> None:
    """推送 Agent 开始事件"""
    data = AgentStartEvent(agent=agent, status=status).model_dump()
    await push_event(event_queue, SSEEventType.AGENT_START, data)


async def push_constraint_result(
    event_queue: asyncio.Queue, constraints: List[str], summary: str
) -> None:
    """推送约束检索结果事件"""
    data = ConstraintResultEvent(constraints=constraints, summary=summary).model_dump()
    await push_event(event_queue, SSEEventType.CONSTRAINT_RESULT, data)


async def push_plan(
    event_queue: asyncio.Queue, tasks: List[str], delegated_agent: Optional[str] = None
) -> None:
    """推送计划事件"""
    data = PlanEvent(tasks=tasks, delegated_agent=delegated_agent).model_dump()
    await push_event(event_queue, SSEEventType.PLAN, data)


async def push_approval_required(
    event_queue: asyncio.Queue, plan: str, agent: str, reason: str
) -> None:
    """推送需要审批事件"""
    data = ApprovalRequiredEvent(plan=plan, agent=agent, reason=reason).model_dump()
    await push_event(event_queue, SSEEventType.APPROVAL_REQUIRED, data)


async def push_tool_call(
    event_queue: asyncio.Queue, tool: str, args: Dict[str, Any] = {}
) -> None:
    """推送 Tool 调用事件"""
    data = ToolCallEvent(tool=tool, args=args).model_dump()
    await push_event(event_queue, SSEEventType.TOOL_CALL, data)


async def push_code(
    event_queue: asyncio.Queue, file: str, content: str
) -> None:
    """推送代码生成事件"""
    data = CodeEvent(file=file, content=content).model_dump()
    await push_event(event_queue, SSEEventType.CODE, data)


async def push_test_result(
    event_queue: asyncio.Queue,
    status: str,
    tests_total: int,
    tests_passed: int,
    errors: Optional[List[Dict]] = None,
) -> None:
    """推送测试结果事件"""
    data = TestResultEvent(
        status=status, tests_total=tests_total, tests_passed=tests_passed, errors=errors
    ).model_dump()
    await push_event(event_queue, SSEEventType.TEST_RESULT, data)


async def push_review_result(
    event_queue: asyncio.Queue, status: str, violations: List[Dict] = []
) -> None:
    """推送审查结果事件"""
    data = ReviewResultEvent(status=status, violations=violations).model_dump()
    await push_event(event_queue, SSEEventType.REVIEW_RESULT, data)


async def push_memory_update(
    event_queue: asyncio.Queue, layers: List[str], message: str
) -> None:
    """推送 Memory 更新事件"""
    data = MemoryUpdateEvent(layers=layers, message=message).model_dump()
    await push_event(event_queue, SSEEventType.MEMORY_UPDATE, data)


async def push_done(event_queue: asyncio.Queue, session_id: str, summary: str) -> None:
    """推送完成事件"""
    data = DoneEvent(session_id=session_id, summary=summary).model_dump()
    await push_event(event_queue, SSEEventType.DONE, data)
    await event_queue.put(None)  # 结束信号


async def push_error(event_queue: asyncio.Queue, message: str) -> None:
    """推送错误事件"""
    data = ErrorEvent(message=message).model_dump()
    await push_event(event_queue, SSEEventType.ERROR, data)
    await event_queue.put(None)  # 结束信号
