from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session, raise_unique_fields_error, search_id
from models.models_db import User
from schema.schemas import (
    HTML_HELLO,
    Message,
    TokenSchema,
    UserList,
    UserPublic,
    UserSchema,
)
from security import get_pwd_hash, verify_pwd

app = FastAPI()


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
    user_db = search_id(user_id, session)
    if user_db:
        user = User(
            id=user_db.id, username=user_db.username, email=user_db.email
        )
        return user


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
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


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    user_db = search_id(user_id, session)
    if user_db:
        test_user = session.scalar(
            select(User).where(
                ((User.username == user.username) | (User.email == user.email))
                & (User.id != user_id)
            )
        )
        if test_user:
            raise_unique_fields_error(user, test_user)

    # Sobrescreve os dados originais do banco com os dados recebidos da API
    user_db.username = user.username
    user_db.email = user.email
    user_db.password = get_pwd_hash(user.password)

    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_db = search_id(user_id, session)

    if user_db:
        session.delete(user_db)
        session.commit()

    return user_db


@app.post('/token/', response_model=TokenSchema)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    # verifica se o email passado é válido
    if not user:
        raise HTTPException(
            detail='incorrect email or password',
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    # verifica se a senha passada corresponde ao hash no banco
    # a mensagem de ambos é igual para evitar que não seja possível saber
    # que uma senha existente não corresponde ao email fornecido,
    # evitando que outros emails sejam inseridos para tentar fazer
    # login com a senha
    if not verify_pwd(form_data.password, user.password):
        raise HTTPException(
            detail='incorrect email or password',
            status_code=HTTPStatus.UNAUTHORIZED,
        )
