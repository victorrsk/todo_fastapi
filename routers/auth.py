from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models.models_db import User
from schema.schemas import (
    TokenSchema,
)
from security import (
    create_access_token,
    verify_pwd,
)

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token/', response_model=TokenSchema)
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

    if not verify_pwd(form_data.password, user.password):
        raise HTTPException(
            detail='incorrect email or password',
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}
