from dataclasses import dataclass, field
from typing import Any

from app.domain.state import DialogueState
from app.task.runner.models.base import ActionResult
from app.task.runner.registry import ActionRegistry

@dataclass(slots=True)
class ActionCall:
    action_name: str
    action_kwargs: dict[str, Any] = field(default_factory=dict)

class ActionRunner:
    def __init__(self, registry: ActionRegistry):
        self.registry = registry

    async def run(self, state: DialogueState, action_call: ActionCall) -> ActionResult:
        # 通过reigstry获取action_call中的action实例
        action = self.registry.get(action_call.action_name)

        # 调用action的run方法
        action_result = await action.run(state, action_call.action_kwargs)

        return action_result



if __name__ == '__main__':
    from app.task.runner.builder import build_action_runner
    from app.domain.messages import MessageType
    from app.domain.messages import UserMessage
    import asyncio

    async def test():
        action_call = ActionCall(
              action_name="action_response",
              action_kwargs={
                "mode": "generate"
            }
        )
        state = DialogueState(sender_id="u1001")
        state.create_session()
        state.create_turn(UserMessage(
            sender_id="u1001",
            message_id="123",
            type=MessageType.TEXT,
            text="你好呀！"
        ))

        runner = build_action_runner()
        result: ActionResult = await runner.run(state, action_call)
        print(result)
    asyncio.run(test())