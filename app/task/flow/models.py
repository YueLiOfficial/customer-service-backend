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

    def get_start_step(self) -> FlowStep:
        for step in self.steps:
            if step.type == "start":
                return step
        return None # type: ignore

@dataclass(slots=True)
class FlowList:
    slots: dict[str, FlowSlot] = field(default_factory=dict)
    flows: list[Flow] = field(default_factory=list)

    def get_flow_by_id(self, flow_id) -> Flow:
        for flow in self.flows:
            if flow.id == flow_id:
                return flow
        return None # type: ignore