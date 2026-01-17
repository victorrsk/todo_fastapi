from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token/', response_model=TokenSchema)
async def login_for_access_token(
    form_data: T_OAuthForm,
    session: T_Session,
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

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
