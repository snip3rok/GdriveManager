from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from db import async_session


class Manager:
    @staticmethod
    async def register_user(session: AsyncSession, user_id, state=None) -> User:
        user = User(uid=user_id, state=state)
        session.add(user)
        await session.commit()
        return user

    @staticmethod
    async def get_user(session: AsyncSession, user_id):
        stmt = select(User).filter(User.uid == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_user_state(user_id):
        async with async_session() as session:
            user = await Manager.get_user(session, user_id)
            return user.state if user is not None else None

    @staticmethod
    async def get_user_token(user_id):
        async with async_session() as session:
            user = await Manager.get_user(session, user_id)
            return user.access_token if user is not None else None



