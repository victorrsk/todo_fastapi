from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database import get_session
from main.app import app
from models.models_db import Base, User
from security import get_pwd_hash


# fixture que retorna um client para testes de rotas da API
@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

    app.dependency_overrides.clear()


# fixture para criação de tabela e abertura de session para operações no bd
@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


# usado para inserir um created_at "falso" no bd
@contextmanager
def _mock_db_time(model, time=datetime(2026, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(target=model, identifier='before_insert', fn=fake_time_hook)
    event.listen(target=model, identifier='before_update', fn=fake_time_hook)

    yield time

    event.remove(target=model, identifier='before_insert', fn=fake_time_hook)
    event.remove(target=model, identifier='before_update', fn=fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session):

    password = 'test123'

    user = User(
        username='test',
        email='test@email.com',
        password=get_pwd_hash(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    # salva a senha limpa para comparar com o hash nos testes de token
    user.clean_pwd = password

    return user


@pytest.fixture
def token(client, user):
    # automaticamente insere um registro no banco de dados
    # usando a fixture user
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_pwd},
    )

    _token = response.json()['access_token']
    return _token
