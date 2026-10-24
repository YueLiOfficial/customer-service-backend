from app.domain.state import DialogueState, Turn
from app.repository.dialogue_state_repo import DialogueStateRepo


class HistoryService:
    def __init__(self, repository: DialogueStateRepo) -> None:
        self.repo = repository

    async def build_history_turns(self, sender_id: str) -> list[Turn]:
        state: DialogueState = await self.repo.load(sender_id)

        sessions = state.sessions

        turns: list[Turn] = []

        for session in sessions:
            turns.extend(session.turns)

        return turns



