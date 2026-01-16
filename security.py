from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models.models_db import User
from settings import Settings

pwd_context = PasswordHash.recommended()

TOKEN_EXPIRE_TIME = Settings().TOKEN_EXPIRE_TIME
SECRET_KEY = Settings().SECRET_KEY
ALGORITHM = Settings().ALGORITHM


def get_pwd_hash(pwd: str):
    return pwd_context.hash(pwd)


def verify_pwd(plain_pwd: str, hashed_pwd: str):
    return pwd_context.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict):
    to_encode = data.copy()
    # soma 30 minutos ao horario UTC atual, zero fuso-horário
    expire_time = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=TOKEN_EXPIRE_TIME
    )
    # inclui a claim de expire no token
    to_encode['exp'] = expire_time
    # cria o token com payload, chave/segredo e o algoritmo
    encoded_jwt = encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


oauth2 = OAuth2PasswordBearer(tokenUrl='/auth/token')


def get_current_user(
    token: str = Depends(oauth2), session: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        detail='could not validate credentials',
        status_code=HTTPStatus.UNAUTHORIZED,
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(token, SECRET_KEY, ALGORITHM)
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == subject_email))
    if not user:
        raise credentials_exception

    return user
