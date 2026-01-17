from http import HTTPStatus

import pytest
from jwt import decode

from security import ALGORITHM, SECRET_KEY, create_access_token


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


def test_nonexistent_email_in_token(client):
    data = {'sub': 'nonexistent@email.com'}
    token = create_access_token(data=data)

    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'could not validate credentials'}
