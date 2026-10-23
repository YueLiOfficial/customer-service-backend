from dataclasses import dataclass
from enum import Enum

from app.domain.state import DialogueState
from app.knowledge.intents import KnowledgeIntent
from app.plan.models import TurnPlan
from app.task.commands.models import ResumeFlowCommand, StartFlowCommand
from app.task.flow.models import FlowList

class ClarifyReason(str, Enum):
    MISSING_TRACK = "missing_track"
    MULTIPLE_TRACKS = "multiple_tracks"
    MISSING_TASK_COMMANDS = "missing_task_commands"
    TASK_FLOW_NOT_EXIST = "task_flow_not_exist"   # 任务轨道中的命令的流程id不存在
    MISSING_KNOWLEDGE_INTENT = "missing_knowledge_intent"
    KNOWLEDGE_INTENT_NOT_EXIST = "knowledge_intent_not_exist"
    MISSING_FOCUSED_OBJECT = "missing_focused_object"
    OBJECT_REQUIRES_INTENT = "object_requires_intent"


@dataclass(slots=True)
class ValidateResult:
    valid: bool
    reason: ClarifyReason | None = None

class TurnPlanValidator:
    def __init__(self) -> None:
        pass

    def validate(
        self, 
        state: DialogueState, 
        plan: TurnPlan, 
        flows: FlowList, 
        intents: dict[str, KnowledgeIntent]
    ) -> ValidateResult:

        # 单轨道判断
        tracks = self._collect_tracks(plan)
        if not tracks:
            return ValidateResult(valid=False, reason=ClarifyReason.MISSING_TRACK)
        elif len(tracks) > 1:
            return ValidateResult(valid=False, reason=ClarifyReason.MULTIPLE_TRACKS)

        # 轨道合法性判断
        if tracks[0] == "task":
            return self._validate_task(plan, flows)
        elif tracks[0] == "knowledge":
            return self._validate_knowledge(state, plan, intents)
        else:
            return ValidateResult(valid=True)

    def _collect_tracks(self, plan: TurnPlan) -> list[str]:
        tracks = []
        if plan.task is not None:
            tracks.append("task")
        if plan.knowledge is not None:
            tracks.append("knowledge")
        if plan.chitchat is not None:
            tracks.append("chitchat")

        return tracks

    def _validate_task(self, plan: TurnPlan, flows: FlowList) -> ValidateResult:
        assert plan.task is not None
        commands = plan.task.commands

        if not commands:
            return ValidateResult(valid=False, reason=ClarifyReason.MISSING_TASK_COMMANDS)

        for command in commands:
            if isinstance(command, (StartFlowCommand, ResumeFlowCommand)):
                is_exist = False
                for flow in flows.flows:
                    if flow.id == command.flow:
                        is_exist = True
                        break

                if not is_exist:
                    return ValidateResult(valid=False, reason=ClarifyReason.TASK_FLOW_NOT_EXIST)

        return ValidateResult(valid=True)

    def _validate_knowledge(self, state: DialogueState, plan: TurnPlan, intents: dict[str, KnowledgeIntent]) -> ValidateResult:
        assert plan.knowledge is not None
        plan_intents = plan.knowledge.intents

        if not plan_intents:
            return ValidateResult(valid=False, reason=ClarifyReason.MISSING_KNOWLEDGE_INTENT)

        for plan_intent in plan_intents:
            if plan_intent not in intents:
                return ValidateResult(valid=False, reason=ClarifyReason.KNOWLEDGE_INTENT_NOT_EXIST)
            
            if plan_intent == "product_info":
                if not state.focused_object or state.focused_object.type == "order":
                    return ValidateResult(valid=False, reason=ClarifyReason.MISSING_FOCUSED_OBJECT)
            elif plan_intent == "order_info":
                if not state.focused_object or state.focused_object.type == "product":
                    return ValidateResult(valid=False, reason=ClarifyReason.MISSING_FOCUSED_OBJECT)

        return ValidateResult(valid=True)
 
