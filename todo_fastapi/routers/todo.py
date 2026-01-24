from http import HTTPStatus
from typing import Annotated

from database import get_session
from fastapi import APIRouter, Depends, Query
from models.models_db import Todo, User
from schema.schemas import (
    FilterPage,
    FilterTodo,
    TodoPublic,
    TodoSchema,
    TodosList,
)
from security import (
    get_current_user,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_FilterPage = Annotated[FilterPage, Query()]
T_FilterTodo = Annotated[FilterTodo, Query()]


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


@router.get('/', status_code=HTTPStatus.OK, response_model=TodosList)
async def read_todos(
    session: T_Session, current_user: T_CurrentUser, filter_todo: T_FilterTodo
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if filter_todo.title:
        query = query.filter(Todo.title.contains(filter_todo.title))
    if filter_todo.description:
        query = query.filter(
            Todo.description.contains(filter_todo.description)
        )
    if filter_todo.state:
        query = query.filter(Todo.state == filter_todo.state)

    todos = await session.scalars(
        query.offset(filter_todo.offset).limit(filter_todo.limit)
    )

    return {'todos': todos.all()}
