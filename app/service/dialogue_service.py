from app.domain.messages import ProcessMessage, UserMessage
from app.engine.dialogue_engine import DialogueEngine
from app.repository.dialogue_state_repo import DialogueStateRepo


class DialogueService:
    def __init__(self, repo: DialogueStateRepo, engine: DialogueEngine) -> None:
        self._repo = repo
        self._engine = engine

    async def process_message(self, message: UserMessage) -> ProcessMessage:
        # 获取历史状态
        state = await self._repo.load(message.sender_id)
        # 调用Engine层处理消息
        precess_msg = self._engine.process(state=state, message=message)
        # 更新历史状态
        await self._repo.save(state)

        return precess_msg
