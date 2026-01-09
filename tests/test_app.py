from http import HTTPStatus

from schema.schemas import HTML_HELLO


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


def test_read_zero_users(client):
    response = client.get('/users')
    assert response.json() == {'users': []}


def test_read_users_with_user(client, user):
    response = client.get('/users/')
    assert response.json() == {
        'users': [
            {'id': user.id, 'username': user.username, 'email': user.email}
        ]
    }
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


def test_update_user_404(client):
    response = client.put(
        '/users/2',
        json={
            'username': 'victor_novo',
            'email': 'emailnovo@email.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_read_user(client):
    response = client.get('/users/1')
    assert response.json() == {
        'id': 1,
        'username': 'victor_novo',
        'email': 'emailnovo@email.com',
    }


def test_read_user_404(client):
    response = client.get('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.json() == {'message': 'user deleted'}


def test_delete_user_404(client):
    response = client.delete('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND
