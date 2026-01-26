from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from database import get_session
from factory import faker, fuzzy
from factory.base import Factory
from factory.declarations import LazyAttribute, Sequence
from fastapi.testclient import TestClient
from main.app import app
from models.models_db import Base, Todo, TodoState, User
from security import get_pwd_hash
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

# -------------------------------DB_connection---------------------------------


# fixture que retorna um client para testes de rotas da API
@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    # se conecta ao banco, cria e apaga tabela em runtime do teste
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as eng:
        await eng.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as eng:
        await eng.run_sync(Base.metadata.drop_all)


# ------------------------------Mock_db_time-----------------------------------


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


# ---------------------------------Fixed_time-------------------------------


@pytest.fixture
def fixed_time():
    # usar dentro da fixture todo e user
    # o datetime padrão é igual ao do mock_db_time
    return datetime(2026, 1, 1)


@pytest.fixture
def fixed_time_iso(fixed_time):
    # retorna fixed_time em string, usar em comparações
    return fixed_time.isoformat()


# -------------------------------Factories---------------------------------


class RandomUser(Factory):
    class Meta:
        model = User

    username = Sequence(lambda num: f'test{num}')
    email = LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = LazyAttribute(lambda obj: f'{obj.username}_password')


class RandomTodo(Factory):
    class Meta:
        model = Todo

    title = faker.Faker('text', max_nb_chars=10)
    description = faker.Faker('text', max_nb_chars=20)
    state = fuzzy.FuzzyChoice(TodoState)
    user_id = 1


# ---------------------------------Todo----------------------------------------


@pytest_asyncio.fixture
async def todo(session, fixed_time):
    _todo = RandomTodo(created_at=fixed_time, updated_at=fixed_time)

    session.add(_todo)
    await session.commit()
    await session.refresh(_todo)

    return _todo


# -------------------------------User---------------------------------


@pytest_asyncio.fixture
async def user(session, fixed_time):

    password = 'test123'

    user = User(
        username='test',
        email='test@email.com',
        password=get_pwd_hash(password),
        created_at=fixed_time,
        updated_at=fixed_time,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    # salva a senha limpa para comparar com o hash nos testes de token
    user.clean_pwd = password

    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'other_test'

    user = RandomUser(password=get_pwd_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_pwd = password

    return user


# -------------------------------Token-----------------------------------


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


@pytest.fixture
def other_token(other_user, client):
    response = client.post(
        '/auth/token',
        data={'username': other_user.email, 'password': other_user.clean_pwd},
    )

    _other_token = response.json()['access_token']

    return _other_token
