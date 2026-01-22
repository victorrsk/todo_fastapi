from http import HTTPStatus

from freezegun import freeze_time
from jwt import decode
from security import (
    ALGORITHM,
    SECRET_KEY,
    TOKEN_EXPIRE_TIME,
    create_access_token,
)


def test_token_creation():
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(jwt=token, key=SECRET_KEY, algorithms=ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded.keys()


def test_get_token(client, user):
    response = client.post(
        'auth/token/',
        data={'username': user.email, 'password': user.clean_pwd},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token.keys()


def test_invalid_token(client):
    response = client.get(
        '/users', headers={'Authorization': 'Bearer <invalid_token>'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'could not validate credentials'}


def test_no_email_in_token_payload(client):
    data = {'invalid': 'payload'}
    token = create_access_token(data=data)

    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'could not validate credentials'}


def test_nonexistent_email_in_db(client):
    data = {'sub': 'nonexistent@email.com'}
    token = create_access_token(data=data)

    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'could not validate credentials'}


def test_nonexistent_user_in_token(client):
    response = client.post(
        '/auth/token',
        data={'username': 'nonexistent@email.com', 'password': 'test123'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'incorrect email or password'}


def test_incorrect_clean_password_in_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'incorrectpwd'},
    )

    assert response.json() == {'detail': 'incorrect email or password'}
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_expired_token_after_time(client, user):
    with freeze_time('2026-01-01  00:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_pwd},
        )

    assert response.status_code == HTTPStatus.OK
    token = response.json()['access_token']

    with freeze_time(f'2026-01-01 00:{TOKEN_EXPIRE_TIME + 5}:00'):
        response = client.get(
            '/users', headers={'Authorization': f'Bearer {token}'}
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'could not validate credentials'}


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert 'token_type' in response.json()
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'Bearer'
