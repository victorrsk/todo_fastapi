from http import HTTPStatus


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
        'created_at': response.json()['created_at'],
        'updated_at': response.json()['updated_at'],
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


def test_read_users(client, user, token, fixed_time_iso):
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )
    # valida o user de acordo com o schema de UserPublic
    # e converte em um dicionário
    assert response.json() == {
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': fixed_time_iso,
                'updated_at': fixed_time_iso,
            }
        ]
    }
    assert response.status_code == HTTPStatus.OK


def test_update_user(client, user, token, fixed_time_iso):
    response = client.put(
        '/users/1',
        json={
            'username': 'new_test',
            'email': 'new_email@email.com',
            'password': 'test123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.json() == {
        'id': 1,
        'username': 'new_test',
        'email': 'new_email@email.com',
        'created_at': fixed_time_iso,
        'updated_at': response.json()['updated_at'],
    }
    assert response.status_code == HTTPStatus.OK


def test_update_user_integrity_error_username(client, user, token):
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
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username already in use'}


def test_update_user_integrity_error_email(client, user, token):
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
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'email already in use'}


def test_read_user(client, user, fixed_time_iso):
    response = client.get(f'/users/{user.id}')
    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@email.com',
        'created_at': fixed_time_iso,
        'updated_at': fixed_time_iso,
    }


def test_read_user_should_return_not_found(
    client,
):
    response = client.get('/users/2')

    assert response.json() == {'detail': 'user not found'}
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client, user, token, fixed_time_iso):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@email.com',
        'created_at': fixed_time_iso,
        'updated_at': fixed_time_iso,
    }


def test_update_other_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        json={
            'username': 'bob',
            'email': 'bob@email.com',
            'password': 'bob_pwd',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'not enough permission'}
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_other_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'detail': 'not enough permission'}
    assert response.status_code == HTTPStatus.FORBIDDEN
