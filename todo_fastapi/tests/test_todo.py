from http import HTTPStatus

import pytest
from factory import faker, fuzzy
from factory.base import Factory
from models.models_db import Todo, TodoState

# ---------------------------- testes de create ---------------------------


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


# ---------------------------- testes de read ---------------------------


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


def test_read_todos_factory(todo, client, token):
    # com fixture
    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'todos': [
            {
                'id': todo.id,
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


# ---------------------------- testes de filtro ---------------------------


def test_title_in_todo_filter(client, token, todo):
    response = client.get(
        f'/todos?title={todo.title}',
        headers={'Authorization': f'Bearer {token}'},
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


def test_description_in_todo_filter(client, token, todo):
    response = client.get(
        f'/todos?description={todo.description}',
        headers={'Authorization': f'Bearer {token}'},
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


def test_state_in_todo_filter(client, token, todo):
    response = client.get(
        f'/todos?state={todo.state.value}',
        headers={'Authorization': f'Bearer {token}'},
    )

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


# ---------------------------- testes de delete ---------------------------


def test_delete_todo(todo, token, client, user):
    response = client.delete(
        f'/todos/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'message': 'deleted'}


def test_delete_nonexistent_todo(client, token):
    response = client.delete(
        '/todos/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'detail': 'todo not found'}


def test_delete_other_user_todo(client, todo, token, other_token):
    response = client.delete(
        'todos/1', headers={'Authorization': f'Bearer {other_token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'not enough permission'}


# ---------------------------- testes de patch ---------------------------


def test_patch_todo(client, token, todo):
    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'new_title'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'new_title'


def test_patch_nonexistent_todo(client, token):
    response = client.patch(
        '/todos/2', json={}, headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'todo not found'}


def test_patch_invalid_state_for_todo(client, token, todo):
    response = client.patch(
        f'/todos/{todo.id}',
        json={'state': 'invalid_state'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'invalid value for todo'}


def test_patch_other_user_todo(client, todo, user, other_token):
    response = client.patch(
        f'/todos/{todo.id}',
        json={},
        headers={'Authorization': f'Bearer {other_token}'},
    )

    assert response.json() == {'detail': 'not enough permission'}
