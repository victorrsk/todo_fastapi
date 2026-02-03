from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from todo_fastapi.database import (
    get_session,
    raise_unique_fields_error,
    search_id,
)
from todo_fastapi.models.models_db import User
from todo_fastapi.schema.schemas import (
    FilterPage,
    UserList,
    UserPublic,
    UserSchema,
)
from todo_fastapi.security import (
    get_current_user,
    get_pwd_hash,
)

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_FilterPage = Annotated[FilterPage, Query()]


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(
    session: T_Session,
    current_user: T_CurrentUser,
    filter_page: T_FilterPage,
):
    users = await session.scalars(
        select(User).offset(filter_page.offset).limit(filter_page.limit)
    )
    return {'users': users}


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def read_user(user_id: int, session: T_Session):
    user_db = await search_id(user_id, session)

    if user_db is None:
        raise HTTPException(
            detail='user not found', status_code=HTTPStatus.NOT_FOUND
        )

    return user_db


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: T_Session):
    user_db = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if user_db:
        raise_unique_fields_error(user, user_db)

    user_db = User(
        username=user.username,
        email=user.email,
        password=get_pwd_hash(user.password),
    )
    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)
    return user_db


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            detail='not enough permission', status_code=HTTPStatus.FORBIDDEN
        )
    test_user = await session.scalar(
        select(User).where(
            ((User.username == user.username) | (User.email == user.email))
            & (User.id != user_id)
        )
    )
    if test_user:
        raise_unique_fields_error(user, test_user)

    # Sobrescreve os dados originais do banco com os dados recebidos da API
    current_user.username = user.username
    current_user.email = user.email
    current_user.password = get_pwd_hash(user.password)

    session.add(current_user)

    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.delete(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            detail='not enough permission', status_code=HTTPStatus.FORBIDDEN
        )

    await session.delete(current_user)
    await session.commit()

    return current_user
