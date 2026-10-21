from dataclasses import field
from typing import Any

from app.task.runner.models.base import Action


class ActionRegistry:
    def __init__(self):
        self._actions: dict[str, Any] = {}

    def register(self, action: Action):
        self._actions[action.name] = action

    def get(self, action_name: str) -> Action:
        if action_name not in self._actions:
            raise KeyError(f"{action_name} 不存在")
        return self._actions[action_name]