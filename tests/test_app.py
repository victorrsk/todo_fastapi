from http import HTTPStatus

from schema.schemas import HTML_HELLO, UserPublic


def test_root_should_return_hello_world(client):
    response = client.get('/')
    assert response.json() == {'message': 'Hello world!'}
    assert response.status_code == HTTPStatus.OK


def test_hello_should_return_meu_endpoint(client):
    response = client.get('/hello')
    assert response.text == HTML_HELLO


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'victor',
            'email': 'victor@email.com',
            'password': 'senhavictor',
        },
    )

    assert response.json() == {
        'id': 1,
        'username': 'victor',
        'email': 'victor@email.com',
    }
    assert response.status_code == HTTPStatus.CREATED


def test_create_user_integrity_error_username(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'test',
            'email': 'test2@email.com',
            'password': 'test123',
        },
    )
    assert response.json() == {'detail': 'username already in use'}
    assert response.status_code == HTTPStatus.CONFLICT


def test_create_user_integrity_error_email(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'new_name',
            'email': 'test@email.com',
            'password': 'test123',
        },
    )
    assert response.json() == {'detail': 'email already in use'}
    assert response.status_code == HTTPStatus.CONFLICT


def test_read_zero_users(client):
    response = client.get('/users')
    assert response.json() == {'users': []}


def test_read_users_with_user(client, user):
    response = client.get('/users/')
    # valida o user de acordo com o schema de UserPublic
    # e converte em um dicionário
    user_schema = UserPublic.model_validate(user).model_dump()
    assert response.json() == {'users': [user_schema]}
    assert response.status_code == HTTPStatus.OK


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'new_test',
            'email': 'new_email@email.com',
            'password': 'test123',
        },
    )
    assert response.json() == {
        'id': 1,
        'username': 'new_test',
        'email': 'new_email@email.com',
    }
    assert response.status_code == HTTPStatus.OK


def test_update_user_integrity_error_username(client, user):
    client.post(
        '/users/',
        json={
            'username': 'walter',
            'email': 'walter@email.com',
            'password': 'w1234',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'walter',
            'email': 'walter@email.com',
            'password': 'test123',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username already in use'}


def test_update_user_integrity_error_email(client, user):
    client.post(
        '/users/',
        json={
            'username': 'walter',
            'email': 'walter@email.com',
            'password': 'w1234',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'new_name',
            'email': 'walter@email.com',
            'password': 'test123',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'email already in use'}


def test_update_user_should_return_not_found(client):
    response = client.put(
        '/users/2',
        json={
            'username': 'victor_novo',
            'email': 'emailnovo@email.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_read_user(client, user):
    response = client.get(f'/users/{user.id}')
    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@email.com',
    }


def test_read_user_should_return_not_found(client):
    response = client.get('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client, user):
    response = client.delete(f'/users/{user.id}')
    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@email.com',
    }


def test_delete_user__should_return_not_found(client):
    response = client.delete('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND
