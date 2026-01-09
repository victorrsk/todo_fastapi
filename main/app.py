from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models.models_db import User
from schema.schemas import (
    HTML_HELLO,
    Message,
    UserDB,
    UserList,
    UserPublic,
    UserSchema,
)

app = FastAPI()

database: list[UserDB] = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello world!'}


@app.get('/hello', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def hello():
    return HTML_HELLO


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    # traz no máximo 10 registros
    session: Session = Depends(get_session),
    limit: int = 10,
    offset: int = 0,
):
    users = session.scalars(select(User).offset(offset).limit(limit))
    return {'users': users}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user(user_id: int, session=Depends(get_session)):

    user_db = session.scalar(select(User).where(User.id == user_id))
    if user_db:
        user = User(
            id=user_db.id, username=user_db.username, email=user_db.email
        )
        return user

    raise HTTPException(detail='not found', status_code=HTTPStatus.NOT_FOUND)


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    # básico
    user_db = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if user_db:
        if user_db.username == user.username:
            raise HTTPException(
                detail='username already in use',
                status_code=HTTPStatus.CONFLICT,
            )
        elif user_db.email == user.email:
            raise HTTPException(
                detail='email already in use', status_code=HTTPStatus.CONFLICT
            )
    user_db = User(
        username=user.username, email=user.email, password=user.password
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


# FIXME inserir um id inválido ou email/username já existente ainda não foi
# tratado corretamente
@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    user_updt = session.scalar(select(User).where(User.id == user_id))
    user_updt.username = user.username
    user_updt.email = user.email
    user_updt.password = user.password
    session.add(user_updt)
    session.commit()
    session.refresh(user_updt)
    return user_updt


@app.delete('/users/{user_id}', status_code=HTTPStatus.OK)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )
    del database[user_id - 1]

    return {'message': 'user deleted'}
