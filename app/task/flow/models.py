from dataclasses import dataclass, field

from app.task.flow.steps import FlowStep

@dataclass(slots=True)
class FlowSlot:
    name: str
    type: str
    label: str
    description: str

@dataclass(slots=True)
class Flow:
    id: str
    name: str
    description: str
    steps: list[FlowStep] = field(default_factory=list)
    slots: list[FlowSlot] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Flow":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            steps=[FlowStep.from_dict(step) for step in data["steps"]]
        )

@dataclass(slots=True)
class FlowList:
    slots: dict[str, FlowSlot] = field(default_factory=dict)
    flows: list[Flow] = field(default_factory=list)