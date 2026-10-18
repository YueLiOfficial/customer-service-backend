import uuid

from app.domain.messages import BotMessage, ProcessMessage, UserMessage


class DialogueService:

    def process_message(self, message: UserMessage) -> ProcessMessage:
        # TODO: 获取历史状态
        # TODO：调用Engine层处理消息
        # TODO：更新历史状态

        return ProcessMessage(
            sender_id=message.sender_id,
            message_id=message.message_id if message.message_id else str(uuid.uuid4()),
            messages=[
                BotMessage(
                    text="你好呀 DialogueService"
                )
            ]
        )
