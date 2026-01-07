from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from main.app import app
from models.models_db import Base


# fixture que retorna um client para testes de rotas da API
@pytest.fixture
def client():
    return TestClient(app)


# fixture para criação de tabela e abertura de session para operações no bd
@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)


# usado para inserir um created_at "falso" no bd
@contextmanager
def _mock_db_time(model, time=datetime(2026, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(target=model, identifier='before_insert', fn=fake_time_hook)

    yield time

    event.remove(target=model, identifier='before_insert', fn=fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
