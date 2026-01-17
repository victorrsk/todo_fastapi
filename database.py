from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session

from models.models_db import User
from schema.schemas import UserSchema
from settings import Settings


async def get_session():
    """_summary_

    Yields:
        Session: give an session object used for making database oporations
    """
    engine = create_async_engine(Settings().DATABASE_URL)

    async with AsyncSession(engine) as session:
        yield session


def raise_unique_fields_error(user: UserSchema, user_db: User):
    """_summary_

    Args:
        user (UserSchema): user received by the API
        user_db (User): user received via database query

    Raises:
        HTTPException: raises an error for usernames already in use
        HTTPException: raises an error for emails already in use

    Returns:
        None: none
    """
    if user.username == user_db.username:
        raise HTTPException(
            detail='username already in use', status_code=HTTPStatus.CONFLICT
        )
    if user.email == user_db.email:
        raise HTTPException(
            detail='email already in use', status_code=HTTPStatus.CONFLICT
        )


def search_id(user_id: int, session: Session | AsyncSession):
    """_summary_

    Args:
        user_id (int): user_id given by parameter
        session (Session): used in the main app via get_session function
        for making database operations

    Raises:
        HTTPException: raises error for invalid id's

    Returns:
        user_db: returns an register if the id was found
    """
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            detail='user not found', status_code=HTTPStatus.NOT_FOUND
        )
    return user_db
