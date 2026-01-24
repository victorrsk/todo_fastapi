from http import HTTPStatus

import pytest
from factory import faker, fuzzy
from factory.base import Factory
from models.models_db import Todo, TodoState


def test_create_todo(client, token):
    response = client.post(
        '/todos',
        json={'title': 'test', 'description': 'test', 'state': 'todo'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'test',
        'description': 'test',
        'state': 'todo',
    }


"""def test_read_todos(client, token):
    # sem fixture
    client.post(
        '/todos',
        json={'title': 'test', 'description': 'test', 'state': 'todo'},
        headers={'Authorization': f'Bearer {token}'},
    )
    client.post(
        '/todos',
        json={'title': 'test', 'description': 'test', 'state': 'todo'},
        headers={'Authorization': f'Bearer {token}'},
    )

    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'todos': [
            {'id': 1, 'title': 'test', 'description': 'test', 'state': 'todo'},
            {
                'id': 2,
                'title': 'test',
                'description': 'test',
                'state': 'todo',
            },
        ]
    }"""


def test__read_todos_factory(todo, client, token):
    # com fixture
    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'todos': [
            {
                'id': 1,
                'title': todo.title,
                'description': todo.description,
                'state': todo.state,
            }
        ]
    }


class RandomTodo(Factory):
    class Meta:
        model = Todo

    title = faker.Faker('text', max_nb_chars=10)
    description = faker.Faker('text')
    state = fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.mark.asyncio
async def test_read_todos_should_return_10_todos(session, client, token):
    TODOS_AMOUNT = 10

    todos = RandomTodo.create_batch(TODOS_AMOUNT)

    session.add_all(todos)
    await session.commit()

    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == TODOS_AMOUNT


def test_delete_todo(todo, token, client, user):
    response = client.delete(
        f'/todos/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'msg': 'deleted'}
