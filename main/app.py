from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

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
def read_users():
    return {'users': database}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(detail='user not found', status_code=404)
    return database[user_id - 1]


# @app.get(
# '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
# )
# def read_user(user_id: int):
#    return database[user_id - 1]


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from models.models_db import User
    from settings import Settings
    
    engine = create_engine(Settings().DATABASE_URL)
    session = Session(engine)
    
    # básico
    user_db = session.scalar(select(User).where(User.username == user.username))
    if user_db:
        raise HTTPException(detail='user already exists', status_code=HTTPStatus.CONFLICT)

    user_db = User(username=user.username, email=user.email, password=user.password)
    session.add(user_db)
    session.commit()

    return user_db

@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )
    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id
    return user_with_id


@app.delete('/users/{user_id}', status_code=HTTPStatus.OK)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )
    del database[user_id - 1]

    return {'message': 'user deleted'}
