import pytest
from sqlmodel import Session, SQLModel, create_engine
from testcontainers.postgres import PostgresContainer

class PostgresTestContainer:
    _container = None
    _engine = None

    @classmethod
    def get_container(cls):
        if cls._container is None:
            cls._container = PostgresContainer("postgres:16-alpine")
            cls._container.start()
        return cls._container

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            cls._engine = create_engine(cls.get_container().get_connection_url())
            SQLModel.metadata.create_all(cls._engine)
        return cls._engine

    @classmethod
    def stop(cls):
        if cls._container:
            cls._container.stop()
            cls._container = None
            cls._engine = None

@pytest.fixture(scope="session")
def db_engine():
    engine = PostgresTestContainer.get_engine()
    yield engine

@pytest.fixture
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session
        # Clean up
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
