from pathlib import Path

from app.engine.dialogue_engine import DialogueEngine
from app.task.commands.processor import CommandProcessor
from app.task.flow.executer import FlowExecuter
from app.task.flow.loader import FlowLoader
from app.task.flow.models import FlowList
from app.task.handler import TaskHandler
from app.task.runner.builder import build_action_runner


def build_engine():
    flow_path1 = Path(__file__).parents[2]/'flow_config'/'user_flows.yaml'
    flow_path2 = Path(__file__).parents[2]/'flow_config'/'system_flows.yaml'
    loader = FlowLoader()
    flows_list:FlowList = loader.load_many([flow_path1,flow_path2])

    return DialogueEngine(
        handler=TaskHandler(
            processor=CommandProcessor(),
            executer=FlowExecuter(
                runner=build_action_runner()
            ),
            flows=flows_list
        )
    )