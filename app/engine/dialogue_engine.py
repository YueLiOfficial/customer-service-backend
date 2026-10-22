import time

from app.chitchat.handler import ChitchatHandler
from app.domain.messages import UserMessage, ProcessMessage
from app.domain.state import DialogueState, BotMessage
from app.knowledge.handler import KnowledgeHandler
from app.plan.models import KnowledgeTurnPlan, TaskTurnPlan, TurnPlan
from app.plan.planner import TurnPlanner
from app.task.commands.models import StartFlowCommand, SetSlotsCommand
from app.task.handler import TaskHandler
from app.task.commands.processor import CommandProcessor


class DialogueEngine:
    def __init__(
        self,
        task_handler: TaskHandler,
        knowledge_handler: KnowledgeHandler,
        chitchat_handler: ChitchatHandler,
        planner: TurnPlanner
    ):
        self.task_handler = task_handler
        self.knowledge_handler = knowledge_handler
        self.chitchat_handler = chitchat_handler
        self.planner = planner

    async def process(self, state: DialogueState, message: UserMessage) -> ProcessMessage:
        # 1. 准备会话
        self._prepare_session(state)
        # 2. 创建turn
        self._create_turn(state, message)
        # 3. 处理消息
        bot_messages: list[BotMessage] = []
        if message.type == "text":
            bot_messages = await self._text_msg_handler(state, message)
        else:
            bot_messages = await self._obj_msg_handler(message)
        # 4. 填充turn
        self._pedding_turn(state, bot_messages)
        # 5. 提交turn
        self._commit_turn(state)
        # 6. 返回ProcessMessage
        return ProcessMessage(
            sender_id=message.sender_id,
            message_id=message.message_id,
            messages=bot_messages
        )

    def _prepare_session(self, state: DialogueState) -> None:
        # 从state中获取 当前的session
        session = state.get_current_session()

        if not session:
            # 如果当前session不存在，则创建新的会话
            state.create_session()
        else:
            # 当前session存在
            now = time.time()
            if now - session.last_activity_at > 60 * 60:
                # session过期，关闭session
                state.close_session(session)
                # 清空上一个session的状态
                state.clear_state()
                # 创建新的会话
                state.create_session()
            else:
                # 直接使用这个会话, 更新会话的活跃时间
                state.update_last_active_time(session)

    def _create_turn(self, state: DialogueState, message: UserMessage) -> None:
        state.create_turn(message)

    async def _text_msg_handler(self, state: DialogueState, message: UserMessage) -> list[BotMessage]:
        # TODO: 调用意图识别组件进行意图识别
        turn_plan = await self.planner.predict(state, self.task_handler._flows, self.knowledge_handler.knowledge_intents)
        print(turn_plan)

        # 调用chitchat_handler
        # bot_messages = await self.chitchat_handler.run(state)

        # return bot_messages
        return [BotMessage(text="测试turnplan")]

    async def _obj_msg_handler(self, message: UserMessage) -> list[BotMessage]:
        
        return [BotMessage(text="处理object消息的流程")]

    def _pedding_turn(self, state: DialogueState, messages: list[BotMessage]) -> None:
        state.fill_turn(messages)

    def _commit_turn(self, state: DialogueState) -> None:
        session = state.get_current_session()
        if session:
            state.commit_turn(session)



