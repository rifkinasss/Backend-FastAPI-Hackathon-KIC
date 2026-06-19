from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401
from app.core.env import build_postgres_url, load_environment


load_environment()


POSTGRES_DATABASE_URL = build_postgres_url()

postgres_engine = None


def get_postgres_engine():
    global postgres_engine

    if postgres_engine is None:
        postgres_engine = create_engine(POSTGRES_DATABASE_URL, pool_pre_ping=True)

    return postgres_engine


def create_db_and_tables():
    SQLModel.metadata.create_all(get_postgres_engine())


def get_session():
    with Session(get_postgres_engine()) as session:
        yield session
