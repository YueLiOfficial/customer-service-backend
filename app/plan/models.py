from dataclasses import dataclass

from app.task.commands.models import Command

@dataclass(slots=True)
class TaskTurnPlan:
    commands: list[Command]

    @classmethod
    def from_dict(cls, data: dict) -> "TaskTurnPlan":
        return cls(
            commands = [Command.from_dict(command_dict_data) for command_dict_data in data.get("commands", [])]
        )

@dataclass(slots=True)
class KnowledgeTurnPlan:
    intents: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeTurnPlan":
        return cls(
            intents=data.get("intents",[])
        )

@dataclass(slots=True)
class ChitchatTurnPlan:
    pass

@dataclass(slots=True)
class TurnPlan:
    task: TaskTurnPlan | None
    knowledge: KnowledgeTurnPlan | None
    chitchat: ChitchatTurnPlan | None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            task = TaskTurnPlan.from_dict(data["task"]) if data.get("task") else None,
            knowledge = KnowledgeTurnPlan.from_dict(data["knowledge"]) if data.get("knowledge") else None,
            chitchat = ChitchatTurnPlan() if data.get("chitchat") else None
        )

if __name__ == '__main__':
    import json
    
    json_str = '{"task": {"commands": [{ "command": "start_flow", "flow": "refund_request" }]},"knowledge": null,"chitchat": null}'
    dict_data = json.loads(json_str)
    turn_plan = TurnPlan.from_dict(dict_data)
    print(turn_plan)
