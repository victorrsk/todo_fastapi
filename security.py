from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import encode
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import get_session

pwd_context = PasswordHash.recommended()


def get_pwd_hash(pwd: str):
    return pwd_context.hash(pwd)


def verify_pwd(plain_pwd: str, hashed_pwd: str):
    return pwd_context.verify(plain_pwd, hashed_pwd)


# tempo em minutos
TOKEN_EXPIRE_TIME = 30
SECRET_KEY = 'key123'
ALGORITHM = 'HS256'


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


oauth2 = OAuth2PasswordBearer(tokenUrl='/token')


def get_current_user(
    token: str = Depends(oauth2), session: Session = Depends(get_session)
): ...
