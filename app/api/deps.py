from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.builder import build_engine
from app.engine.dialogue_engine import DialogueEngine
from app.repository.dialogue_state_repo import DialogueStateRepo
from app.service.dialogue_service import DialogueService
from app.infra import database

async def get_session():
    async with database.session_factory() as session: # type: ignore
        yield session

def get_dialogue_state_repo(session: AsyncSession = Depends(get_session)):
    return DialogueStateRepo(session)

def get_dialogue_engine():
    return build_engine()

def get_dialogue_service(
    repo: DialogueStateRepo = Depends(get_dialogue_state_repo),
    engine: DialogueEngine = Depends(get_dialogue_engine)
):
    return DialogueService(repo, engine)