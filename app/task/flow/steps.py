from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from app.task.flow.links import ConditionalFlowLink, FLowLink, FallbackFlowLink, StaticFlowLink

class FlowStepType(str, Enum):
    START = "start"
    ACTION = "action"
    COLLECT = "collect"
    END = "end"

@dataclass(slots=True)
class ResponseDef:
    mode: str = "static"
    text: str | None = None
    prompt: str | None = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data) -> "ResponseDef":
        return cls(**data)

@dataclass(slots=True)
class SlotValidation:
    condition: str
    failure_response: ResponseDef | None = None

    @classmethod
    def from_dict(cls, data) -> "SlotValidation":
        return cls(
            condition=data["condition"],
            failure_response=ResponseDef.from_dict(data["failure_response"]) if data.get("failure_response") else None
        )

@dataclass(slots=True)
class FlowStep:
    id: str
    type: FlowStepType
    next: list[FLowLink] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, data) -> "FlowStep":
        type = data["type"]
        if type == "start":
            return StartFlowStep.from_dict(data)
        elif type == "action":
            return ActionFlowStep.from_dict(data)
        elif type == "collect":
            return CollectFlowStep.from_dict(data)
        else:
            return EndFlowStep.from_dict(data)


@dataclass(slots=True)
class StartFlowStep(FlowStep):
    @classmethod
    def from_dict(cls, data) -> FlowStep:
        return cls(
            id=data["id"],
            type=FlowStepType.START,
            next=build_next(data.get("next")),
            description=data.get("description", "")
        )

@dataclass(slots=True)
class ActionFlowStep(FlowStep):
    action: str = ""
    args: dict[str, Any] | str = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data) -> FlowStep:
        return cls(
            id=data["id"],
            type=FlowStepType.START,
            next=build_next(data.get("next")),
            description=data.get("description", ""),
            action=data.get("action", ""),
            args=data.get("args") if data.get("args") else {}
        )

@dataclass(slots=True)
class CollectFlowStep(FlowStep):
    slot_name: str = ""
    response: ResponseDef = field(default_factory=ResponseDef)
    validation: SlotValidation | None = None

    @classmethod
    def from_dict(cls, data) -> FlowStep:
        return cls(
            id=data["id"],
            type=FlowStepType.START,
            next=build_next(data.get("next")),
            description=data.get("description", ""),
            slot_name=data.get("slot_name"),
            response=ResponseDef.from_dict(data["response"]) if data.get("response") else ResponseDef(),
            validation=SlotValidation.from_dict(data["validation"]) if data.get("validation") else None
        )

@dataclass(slots=True)
class EndFlowStep(FlowStep):
    @classmethod
    def from_dict(cls, data) -> FlowStep:
        return cls(
            id=data["id"],
            type=FlowStepType.START,
            next=[],
            description=data.get("description", "")
        )

def build_next(data: list | str) -> list[FLowLink]:
    flowlink = []
    if isinstance(data, list):
        for link in data:
            if link.get("if"):
                flowlink.append(ConditionalFlowLink(
                    condition=link.get("if"),
                    target=link.get("then")
                ))
            elif link.get("else"):
                flowlink.append(FallbackFlowLink(
                    target=link.get("else")
                ))
    else:
        flowlink.append(StaticFlowLink(
            target=data
        ))

    return flowlink