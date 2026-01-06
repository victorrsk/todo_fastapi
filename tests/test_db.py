from sqlalchemy import select

from models.models_db import User


def test_create_user(session):
    test_user = User(
        username='teste', email='teste@email.com', password='teste123'
    )
    session.add(test_user)
    session.commit()
    user = session.scalar(select(User).where(User.username == 'teste'))
    assert user.username == 'teste'
