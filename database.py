from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from settings import Settings


# inicia conexão com BD e fornece session para realizar as operações
def get_session():
    engine = create_engine(Settings().DATABASE_URL)

    with Session(engine) as session:
        yield session
