import pytest
from fastapi.testclient import TestClient

from main.app import app


@pytest.fixture
def client():
    return TestClient(app)
