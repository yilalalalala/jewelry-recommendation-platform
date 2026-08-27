import os

os.environ["DATABASE_URL"] = "sqlite:///./test_jewelrank.db"

import pytest
from fastapi.testclient import TestClient

from jewelrank.api import app
from jewelrank.database import SessionLocal, engine
from jewelrank.models import Base


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def session():
    with SessionLocal() as db_session:
        yield db_session
