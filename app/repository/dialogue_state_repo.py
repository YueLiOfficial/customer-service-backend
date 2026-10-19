import asyncio
import json

from app.domain.state import DialogueState
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.models.dialogue_state_orm import DialogueStateRecord


class DialogueStateRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def load(self, sender_id: str) -> DialogueState:
        # 通过sender_id 查找对应的state
        result = await self.__session.get(DialogueStateRecord, sender_id)
        # 将state_json 转换成DialogueState
        if result:
            state_dict: dict = json.loads(result.state_json)
            return DialogueState.from_dict(state_dict)
        else:
            return DialogueState(sender_id=sender_id)

    async def save(self, state: DialogueState) -> None:
        # 将state转换成json对象
        state_json = json.dumps(state.to_dict())

        # 查询数据库中是否有这个用户的数据
        result = await self.__session.get(DialogueStateRecord, state.sender_id)
        # 如果之前数据库没数据则插入，有数据则覆盖
        if result:
            result.state_json = state_json
        else:
            recod = DialogueStateRecord(sender_id=state.sender_id, state_json=state_json)
            self.__session.add(recod)

        await self.__session.commit()


if __name__ == "__main__":
    from app.infra import database

    async def test_load():
        database.init_db_engine()

        async with database.session_factory() as session: # type: ignore
            repo = DialogueStateRepo(session)
            state = await repo.load("u1001")
            print(state)

        await database.close_db_engine()

    async def test_save():
        database.init_db_engine()

        async with database.session_factory() as session: # type: ignore
            repo = DialogueStateRepo(session)

            state = DialogueState(
                sender_id="u1002"
            )

            await repo.save(state)

        await database.close_db_engine()

    asyncio.run(test_save())