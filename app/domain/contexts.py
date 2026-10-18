from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class TaskContext:
    flow_id: str
    step_id: str
    slots: dict[str,Any] = field(default_factory=dict)

@dataclass(slots=True)
class SystemContext:
    flow_id: str
    step_id: str

@dataclass(slots=True)
class ResumedSystemContext(SystemContext):
    """system_task_resumed 系统上下文"""
    
    resumed_flow_id: str
    resumed_flow_name: str

@dataclass(slots=True)
class StartedSystemContext(SystemContext):
    """system_task_started 系统上下文"""

    start_flow_id: str
    start_flow_name: str

@dataclass(slots=True)
class CanceledSystemContext(SystemContext):
    """system_task_canceled 系统任务上下文 (当用户任务在执行过程中被取消时)"""
    
    canceled_flow_id: str
    canceled_flow_name: str

@dataclass(slots=True)
class InterruptedSystemContext(SystemContext):
    """system_task_interrupted 系统任务上下文"""

    interrupted_flow_id: str
    interrupted_flow_name: str
    started_flow_id: str | None = None
    started_step_name: str | None = None

@dataclass(slots=True)
class ConnotHandlerSystemContext(SystemContext):
    """system_cannot_handle 系统任务上下文 (当用户任务在执行过程中无法处理时，需要调用此系统任务生成回复消息)"""

    reason: str | None = None

@dataclass(slots=True)
class CollectSystemContext(SystemContext):
    """system_collect_information 系统任务上下文 (当用户任务在执行过程需要收集数据槽位时，需要调用此系统任务)"""

    slot_name: str
    response: dict | None = field(default_factory=dict)
