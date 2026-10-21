from typing import Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import jinja2

from app.domain.messages import BotMessage
from app.domain.state import DialogueState
from app.prompts.history_builder import build_history
from app.task.runner.models.base import Action, ActionResult
from app.infra.llm_client import llm
        
class ActionListen(Action):
    name = "action_listen"

    async def run(self, state: DialogueState, args: dict[str, Any]) -> ActionResult:
        ...

class ActionResponse(Action):
    name = "action_response"

    async def run(self, state: DialogueState, args: dict[str, Any]) -> ActionResult:
        mode = args.get("mode", "static")
        if mode == "rephrase":
            # 改写模式
            text = args.get("text", "")
            render_text = jinja2.Template(text).render(
                slots = state.active_task.slots if state.active_task else {},
                context = state.active_system_task if state.active_system_task else {}              
            )

            prompt = """你是一个中文电商客服助手，语气自然、友好、简洁。
                          请基于下面的建议回复，生成一句更自然的中文回复，保持原意，不要扩写。
                          对话上下文：
                          {{ history }}
                          用户最后一句：
                          用户：{{ user_message }}
                          建议回复：{{ current_response }}
                          改写后的回复："""

            history = build_history(state.get_current_session().turns) # type: ignore
            assert state.pending_turn is not None
            user_message = state.pending_turn.input_message
            prompt_inputs = {
                "history": history,
                "user_message": user_message,
                "current_response": render_text
            }

            prompt_template = PromptTemplate.from_template(
                template=prompt,
                template_format="jinja2"
            )

            chain = prompt_template | llm | StrOutputParser()
            res = await chain.ainvoke(prompt_inputs)

            return ActionResult(
                messages=[BotMessage(res)]
            )

        elif mode == "generate":
            # 生成模式  
            prompt = """你是一个中文电商客服助手，语气自然、友好、简洁。
                          请基于下面的对话历史和用户消息，生成一句回复消息。
                          对话上下文：
                          {{ history }}
                          用户消息：
                          {{ user_message }}
                          生成的回复消息："""

            history = build_history(state.get_current_session().turns) # type: ignore
            assert state.pending_turn is not None
            user_message = state.pending_turn.input_message
            prompt_inputs = {
                "history": history,
                "user_message": user_message,
            }

            prompt_template = PromptTemplate.from_template(
                template=prompt,
                template_format="jinja2"
            )

            chain = prompt_template | llm | StrOutputParser()
            res = await chain.ainvoke(prompt_inputs)

            return ActionResult(
                messages=[BotMessage(res)]
            )
            
        else:
            # 静态模式
            text = args.get("text", "")
            render_text = jinja2.Template(text).render(
                slots = state.active_task.slots if state.active_task else {},
                context = state.active_system_task if state.active_system_task else {}
            )

            return ActionResult(
                messages=[BotMessage(text=render_text)]
            )        

