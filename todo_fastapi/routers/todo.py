from http import HTTPStatus
from typing import Annotated

from database import get_session
from fastapi import APIRouter, Depends, HTTPException, Query
from models.models_db import Todo, TodoState, User
from schema.schemas import (
    FilterPage,
    FilterTodo,
    Message,
    TodoPublic,
    TodoSchema,
    TodosList,
    TodoUpdate,
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


@router.patch(
    '/{todo_id}', status_code=HTTPStatus.OK, response_model=TodoPublic
)
async def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    current_user: T_CurrentUser,
    session: T_Session,
):
    todo_db = await session.scalar(select(Todo).where(Todo.id == todo_id))

    if not todo_db:
        raise HTTPException(
            detail='todo not found', status_code=HTTPStatus.NOT_FOUND
        )

    if todo_db.user_id == current_user.id:
        for key, value in todo.model_dump(exclude_unset=True).items():
            # valida se o valor de state recebido pela API é válido
            if key == 'state' and value not in TodoState:
                raise HTTPException(
                    detail='invalid value for todo',
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            setattr(todo_db, key, value)

        session.add(todo_db)
        await session.commit()
        await session.refresh(todo_db)

        return todo_db

    raise HTTPException(
        detail='not enough permission', status_code=HTTPStatus.FORBIDDEN
    )


@router.delete('/{todo_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_todo(
    todo_id: int, current_user: T_CurrentUser, session: T_Session
):
    todo = await session.scalar(select(Todo).where(Todo.id == todo_id))

    if not todo:
        raise HTTPException(
            detail='todo not found', status_code=HTTPStatus.NOT_FOUND
        )

    if todo.user_id == current_user.id:
        await session.delete(todo)
        await session.commit()

        return {'message': 'deleted'}

    raise HTTPException(
        detail='not enough permission', status_code=HTTPStatus.FORBIDDEN
    )
