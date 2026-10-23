import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.domain.messages import BotMessage
from app.domain.state import DialogueState, FocusedObject
from app.plan.validator import ClarifyReason
from app.prompts.history_builder import _build_user_text, build_history
from app.prompts.prompt_loader import load_prompt
from app.infra.llm_client import llm


class ClarifyResponder:

    async def respond(self, state: DialogueState, reason: ClarifyReason) -> list[BotMessage]:
        clarify_message = self.build_clarify_message(reason, state)

        prompt = load_prompt("clarify")

        assert state.pending_turn is not None
        prompt_inputs = {
            "reason": reason.value,
            "clarify_message": clarify_message,
            "focused_object": json.dumps(state.focused_object.to_dict()) if state.focused_object else None,
            "history": build_history(state.get_current_session().turns), # type: ignore
            "user_message": _build_user_text(state.pending_turn.input_message)
        }

        template = PromptTemplate.from_template(
            prompt,
            template_format="jinja2"
        )

        chain = template | llm | StrOutputParser()
        res = await chain.ainvoke(prompt_inputs)

        return [BotMessage(text=res)]

    def build_clarify_message(self, reason: ClarifyReason, state: DialogueState) -> str:
        if reason is ClarifyReason.MISSING_TRACK:
            return "我没有从你的消息中识别出你的操作目的，请明确告诉我你想做什么"
        if reason is ClarifyReason.MULTIPLE_TRACKS:
            return "你这次同时提到了多个方向。我们先处理一个，你想先办业务还是先咨询信息呢？"
        if reason is ClarifyReason.MISSING_TASK_COMMANDS:
            return "你这次是想办理什么业务呢？比如查订单、查物流，或者申请退款。"
        if reason is ClarifyReason.TASK_FLOW_NOT_EXIST:
            return "智能客服暂不支持此业务办理。目前支持查订单、查物流，或者申请退款等操作"
        if reason is ClarifyReason.MISSING_KNOWLEDGE_INTENT:
            return "你是想了解商品信息、订单信息，还是售后配送规则呢？"
        if reason is ClarifyReason.KNOWLEDGE_INTENT_NOT_EXIST:
            return "智能客服暂不支持此知识意图。目前支持商品信息、订单信息，或者售后配送规则等查询"
        if reason is ClarifyReason.MISSING_FOCUSED_OBJECT:
            return "请先发送你想咨询的商品或订单，我再继续帮你看。"

        if reason is ClarifyReason.OBJECT_REQUIRES_INTENT:
            focused_object = state.focused_object
            if focused_object is not None and focused_object.type == "order":
                return "我已经收到这个订单了。你想查订单状态、查物流，还是申请退款呢？"
            if focused_object is not None and focused_object.type == "product":
                return "我已经收到这个商品了。你想了解它的商品信息、发货情况，还是售后相关问题呢？"

        return "我还需要再确认一下你的意思，你可以换个更具体的说法告诉我。"