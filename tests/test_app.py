from http import HTTPStatus

from fastapi.testclient import TestClient

from main.app import app
from schema.schemas import HTML_HELLO


def test_root_should_return_hello_world():
    client = TestClient(app)
    response = client.get('/')
    assert response.json() == {'message': 'Hello world!'}
    assert response.status_code == HTTPStatus.OK


def test_hello_should_return_meu_endpoint():
    client = TestClient(app)
    response = client.get('/hello')
    assert response.text == HTML_HELLO
