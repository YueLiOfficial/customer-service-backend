from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass(slots=True)
class TaskContext:
    flow_id: str
    step_id: str
    slots: dict[str,Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TaskContext":
        return cls(**data)

@dataclass(slots=True)
class SystemContext:
    flow_id: str
    step_id: str

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "SystemContext":
        flow_id = data["flow_id"]
        return SYSTEM_CONTEXT_MAP.get(flow_id).from_dict(data) # type: ignore

@dataclass(slots=True)
class ResumedSystemContext(SystemContext):
    """system_task_resumed 系统上下文"""
    
    resumed_flow_id: str
    resumed_flow_name: str

    def to_dict(self) -> dict:
        return {
            "flow_id": self.flow_id,
            "step_id": self.step_id,
            "resumed_flow_id": self.resumed_flow_id,
            "resumed_flow_name": self.resumed_flow_name
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResumedSystemContext":
        return cls(**data)

@dataclass(slots=True)
class StartedSystemContext(SystemContext):
    """system_task_started 系统上下文"""

    started_flow_id: str
    started_flow_name: str
    
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "StartedSystemContext":
        return cls(**data)    

@dataclass(slots=True)
class CanceledSystemContext(SystemContext):
    """system_task_canceled 系统任务上下文 (当用户任务在执行过程中被取消时)"""
    
    canceled_flow_id: str
    canceled_flow_name: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CanceledSystemContext":
        return cls(**data)
    
@dataclass(slots=True)
class InterruptedSystemContext(SystemContext):
    """system_task_interrupted 系统任务上下文"""

    interrupted_flow_id: str
    interrupted_flow_name: str
    started_flow_id: str | None = None
    started_flow_name: str | None = None
    resumed_flow_id: str | None = None
    resumed_flow_name: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "InterruptedSystemContext":
        return cls(**data)
    
@dataclass(slots=True)
class CannotHandleSystemContext(SystemContext):
    """system_cannot_handle 系统任务上下文 (当用户任务在执行过程中无法处理时，需要调用此系统任务生成回复消息)"""

    reason: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CannotHandleSystemContext":
        return cls(**data)
    
@dataclass(slots=True)
class CollectSystemContext(SystemContext):
    """system_collect_information 系统任务上下文 (当用户任务在执行过程需要收集数据槽位时，需要调用此系统任务)"""

    slot_name: str
    response: dict | None = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CollectSystemContext":
        return cls(**data)
    
SYSTEM_CONTEXT_MAP = {
    "system_task_resumed": ResumedSystemContext,
    "system_task_interrupted": InterruptedSystemContext,
    "system_task_started": StartedSystemContext,
    "system_collect_information": CollectSystemContext,
    "system_cannot_handle": CannotHandleSystemContext,
    "system_task_canceled": CanceledSystemContext
}
