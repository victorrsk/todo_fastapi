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


def test_read_users(client):
    response = client.get('/users')
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'victor',
                'email': 'victor@email.com'
            }
        ]
    }
    assert response.status_code == HTTPStatus.OK
