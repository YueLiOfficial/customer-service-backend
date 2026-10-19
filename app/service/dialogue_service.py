import uuid

from app.domain.messages import BotMessage, ProcessMessage, UserMessage
from app.repository.dialogue_state_repo import DialogueStateRepo


class DialogueService:
    def __init__(self, repo: DialogueStateRepo) -> None:
        self.__repo = repo

    async def process_message(self, message: UserMessage) -> ProcessMessage:
        # 获取历史状态
        state = await self.__repo.load(message.sender_id)
        print(state)
        # TODO：调用Engine层处理消息
        # 更新历史状态
        await self.__repo.save(state)

        return ProcessMessage(
            sender_id=message.sender_id,
            message_id=message.message_id if message.message_id else str(uuid.uuid4()),
            messages=[
                BotMessage(
                    text="你好呀 DialogueService"
                )
            ]
        )
