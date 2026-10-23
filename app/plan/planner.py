from dataclasses import asdict
import json
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.domain.state import DialogueState
from app.knowledge.intents import KnowledgeIntent
from app.plan.models import TurnPlan
from app.prompts.history_builder import _build_user_text, build_history
from app.prompts.prompt_loader import load_prompt
from app.task.flow.models import FlowList
from app.infra.llm_client import llm


class TurnPlanner:
    def __init__(self) -> None:
        pass

    async def predict(self, state: DialogueState, flow_list: FlowList, intents: dict[str, KnowledgeIntent]) -> TurnPlan:
        prompt = load_prompt("turn_plan")

        flows = [{k:v for k, v in asdict(flow).items() if k != "steps"} for flow in flow_list.flows]
        intent_list = [{"id": intent.id_, "description": intent.description} for intent in intents.values()]

        assert state.pending_turn is not None
        prompt_inputs = {
            "available_flows_json":json.dumps(flows, ensure_ascii=False),
            "knowledge_intents_json":json.dumps(intent_list, ensure_ascii=False),
            "active_task_json":json.dumps(state.active_task.to_dict() if state.active_task else None),
            "interrupted_tasks_json":json.dumps([task.to_dict() for task in state.paused_tasks] if state.paused_tasks else None),
            "focused_object_json":json.dumps(state.focused_object.to_dict() if state.focused_object else None),
            "current_conversation":build_history(state.get_current_session().turns), # type: ignore
            "user_message":_build_user_text(state.pending_turn.input_message),
        }

        template = PromptTemplate.from_template(
            prompt,
            template_format="jinja2"
        )

        chain = template | llm | JsonOutputParser()

        res = await chain.ainvoke(prompt_inputs)

        return TurnPlan.from_dict(res)
