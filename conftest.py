# this file is used to initialize all features used in testing section

import pytest
import asyncio
from main import app


@pytest.fixture(scope="session")
def quart_app():
    return app


@pytest.fixture(scope="session")
def client_id():
    return "1910045535"

# event_loop is to solve pytest-asyncio problem -> RuntimeError: Event loop is closed


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
