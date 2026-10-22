from app.domain.messages import BotMessage, UserMessage
from app.domain.state import Turn
from app.prompts.history_builder import _build_user_text, build_history
from app.prompts.prompt_loader import load_prompt
from app.infra.llm_client import llm

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ChitchatResponder:
    def __init__(self) -> None:
        pass

    async def run(self, turns: list[Turn], message: UserMessage) -> list[BotMessage]:
        # 加载提示词并渲染
        prompt_text = load_prompt("chitchat_respond")

        prompt_input = {
            "history": build_history(turns),
            "user_message": _build_user_text(message)
        }

        prompt_template = PromptTemplate.from_template(
            prompt_text,
            template_format="jinja2"
        )

        chains = prompt_template | llm | StrOutputParser()

        res = await chains.ainvoke(prompt_input)

        return [BotMessage(text=res)]