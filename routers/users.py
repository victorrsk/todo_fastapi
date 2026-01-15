from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session, raise_unique_fields_error, search_id
from models.models_db import User
from schema.schemas import (
    UserList,
    UserPublic,
    UserSchema,
)
from security import (
    get_current_user,
    get_pwd_hash,
)

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    # traz no máximo 10 registros
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
):
    users = session.scalars(select(User).offset(offset).limit(limit))
    return {'users': users}


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id: int, session=Depends(get_session)):
    user_db = search_id(user_id, session)
    if user_db:
        user = User(
            id=user_db.id, username=user_db.username, email=user_db.email
        )
        return user


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    # básico
    user_db = session.scalar(
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
    session.commit()
    session.refresh(user_db)
    return user_db


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            detail='not enough permission', status_code=HTTPStatus.FORBIDDEN
        )
    test_user = session.scalar(
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
    session.commit()
    session.refresh(current_user)
    return current_user


@router.delete(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            detail='not enough permission', status_code=HTTPStatus.FORBIDDEN
        )

    session.delete(current_user)
    session.commit()

    return current_user
