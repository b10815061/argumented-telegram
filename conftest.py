import pytest
from main import app

@pytest.fixture(scope="session")
def quart_app():
    return app

@pytest.fixture(scope="session")
def client_id():
    return "1910045535"