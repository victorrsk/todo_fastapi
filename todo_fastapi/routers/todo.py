from http import HTTPStatus
from typing import Annotated

from database import get_session
from fastapi import APIRouter, Depends, Query
from models.models_db import Todo, User
from schema.schemas import FilterPage, TodoPublic, TodoSchema
from security import (
    get_current_user,
)
from sqlalchemy.ext.asyncio import AsyncSession

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_FilterPage = Annotated[FilterPage, Query()]


router = APIRouter(prefix='/todos', tags=['todos'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema, session: T_Session, current_user: T_CurrentUser
):
    todo_db = Todo(
        title=todo.title, description=todo.description, state=todo.state
    )
    todo_db.user_id = current_user.id
    session.add(todo_db)
    await session.commit()
    await session.refresh(todo_db)

    return todo_db
