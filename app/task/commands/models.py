from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Command:
    command: str

    @classmethod
    def from_dict(cls, data: dict) -> "Command":
        command = data.get("command", '')
        return COMMAND_MAP[command].from_dict(data)

@dataclass(slots=True)
class StartFlowCommand(Command):
    flow: str

    @classmethod
    def from_dict(cls, data: dict) -> "StartFlowCommand":
        return cls(**data)

@dataclass(slots=True)
class CancelFlowCommand(Command):

    @classmethod
    def from_dict(cls, data: dict) -> "CancelFlowCommand":
        return cls(**data)

@dataclass(slots=True)
class ResumeFlowCommand(Command):
    flow: str

    @classmethod
    def from_dict(cls, data: dict) -> "ResumeFlowCommand":
        return cls(**data)

@dataclass(slots=True)
class SetSlotsCommand(Command):
    solts: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict) -> "SetSlotsCommand":
        return cls(**data)

COMMAND_MAP={
    "start_flow": StartFlowCommand,
    "cancel_flow": CancelFlowCommand,
    "resume_flow": ResumeFlowCommand,
    "set_slots": SetSlotsCommand,
}