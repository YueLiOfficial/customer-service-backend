from app.chitchat.responder import ChitchatResponder
from app.domain.messages import BotMessage, UserMessage
from app.domain.state import DialogueState


class ChitchatHandler:
    def __init__(self, responder: ChitchatResponder) -> None:
        self.responder = responder

    async def run(self, state: DialogueState) -> list[BotMessage]:

        assert state.pending_turn is not None
        res = await self.responder.run(
            turns=state.get_current_session().turns, # type: ignore
            message=state.pending_turn.input_message
        )

        return res
