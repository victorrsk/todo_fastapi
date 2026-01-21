import pytest
from models.models_db import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        test_user = User(
            username='teste', email='teste@email.com', password='teste123'
        )
        session.add(test_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'teste'))
    # a forma mais limpa de fazer isso seria usando asdict() do dataclass
    # mas eu usei declarative base e não @mapped_as_dataclass no registry
    # na criação do modelo

    assert user.id == 1
    assert user.username == 'teste'
    assert user.email == 'teste@email.com'
    assert user.password == 'teste123'
    assert user.created_at == time
    assert user.updated_at == time
