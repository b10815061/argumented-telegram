import pytest
from quart import Quart
import json

# not tested in conn: /disconnect, /verify, /logout


@pytest.mark.asyncio
async def test_login(quart_app: Quart):
    client = quart_app.test_client()
    data = {"phone": "+8860909855200"}
    response = await client.post('/login', json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 202


@pytest.mark.asyncio
async def test_check_connection(quart_app: Quart, client_id: str):
    client = quart_app.test_client()
    data = {"uid": client_id}
    response = await client.post('/checkConnection', json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200
