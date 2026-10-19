from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.dialogue_state_repo import DialogueStateRepo
from app.service.dialogue_service import DialogueService
from app.infra import database

async def get_session():
    async with database.session_factory() as session: # type: ignore
        yield session

def get_dialogue_state_repo(session: AsyncSession = Depends(get_session)):
    return DialogueStateRepo(session)

def get_dialogue_service(repo: DialogueStateRepo = Depends(get_dialogue_state_repo)):
    return DialogueService(repo)