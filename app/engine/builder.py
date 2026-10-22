from pathlib import Path

from app.chitchat.handler import ChitchatHandler
from app.chitchat.responder import ChitchatResponder
from app.engine.dialogue_engine import DialogueEngine
from app.knowledge.handler import KnowledgeHandler
from app.knowledge.responder import KnowledgeResponder
from app.task.commands.processor import CommandProcessor
from app.task.flow.executer import FlowExecuter
from app.task.flow.loader import FlowLoader
from app.task.flow.models import FlowList
from app.task.handler import TaskHandler
from app.task.runner.builder import build_action_runner
from app.knowledge.intents import KNOWLEDGE_INTENTS
from app.knowledge.builder import build_provider_registry


def build_engine():
    flow_path1 = Path(__file__).parents[2]/'flow_config'/'user_flows.yaml'
    flow_path2 = Path(__file__).parents[2]/'flow_config'/'system_flows.yaml'
    loader = FlowLoader()
    flows_list:FlowList = loader.load_many([flow_path1,flow_path2])

    return DialogueEngine(
        task_handler=TaskHandler(
            processor=CommandProcessor(),
            executer=FlowExecuter(
                runner=build_action_runner()
            ),
            flows=flows_list
        ),
        knowledge_handler=KnowledgeHandler(
            knowledge_intents=KNOWLEDGE_INTENTS,
            registry=build_provider_registry(),
            responder=KnowledgeResponder()
        ),
        chitchat_handler=ChitchatHandler(
            responder=ChitchatResponder()
        )
    )