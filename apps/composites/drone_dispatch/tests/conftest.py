import pytest
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
from fastapi.testclient import TestClient
from shared.testing import PostgresContainer
from shared.database import get_session

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer() as container:
        yield container

@pytest.fixture(name="session")
def session_fixture(postgres_container):
    engine = create_engine(postgres_container.get_connection_url())
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session):
    from apps.composites.drone_dispatch.main import app
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
