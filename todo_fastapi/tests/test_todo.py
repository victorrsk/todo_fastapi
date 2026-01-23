from http import HTTPStatus


def test_create_todo(client, token, user):
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
