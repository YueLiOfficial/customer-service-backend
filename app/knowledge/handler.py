from app.domain.messages import BotMessage
from app.domain.state import DialogueState
from app.knowledge.intents import KnowledgeIntent
from app.knowledge.registry import ProviderRegistry
from app.knowledge.responder import KnowledgeResponder


class KnowledgeHandler:
    def __init__(
        self,
        knowledge_intents: dict[str, KnowledgeIntent],
        registry: ProviderRegistry,
        responder: KnowledgeResponder
    ) -> None:
        self.knowledge_intents = knowledge_intents
        self.registry = registry
        self.responder = responder

    async def run(self, state: DialogueState, intents: list[str]) -> list[BotMessage]:
        # 遍历intents获取每一个intent
        provider_ids = []
        for intent in intents:
            # 根据intent_id获取到对应的provider_ids
            knowledge_intent = self.knowledge_intents.get(intent)
            if knowledge_intent:
                provider_ids.extend(knowledge_intent.provider_ids)

        chunks = []
        # 根据provier_ids 获取对应的provider实例
        for id_ in provider_ids:
            provider = self.registry.get(id_)
            # 执行provider，获取结果
            cur_chunks = await provider.retrieve(state)
            chunks.extend(cur_chunks)

        assert state.pending_turn is not None
        bot_message = await self.responder.run(
            turns=state.get_current_session().turns, # type: ignore
            message=state.pending_turn.input_message,
            chunks=chunks
        )

        return bot_message