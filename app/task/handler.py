from app.domain.messages import BotMessage
from app.domain.state import DialogueState
from app.task.commands.models import Command
from app.task.commands.processor import CommandProcessor
from app.task.flow.executer import FlowExecuter
from app.task.flow.models import FlowList


class TaskHandler:
    def __init__(
        self, 
        processor: CommandProcessor, 
        executer: FlowExecuter,
        flows: FlowList
    ):
        self._processor = processor
        self._executer = executer
        self._flows = flows

    async def run(self, state: DialogueState, commands: list[Command]) -> list[BotMessage]:
        # 调用commandProcessor进行命令处理
        self._processor.run(commands, state, self._flows)
        # 调用FlowExecuter进行流程推进
        return await self._executer.run(state, self._flows)

