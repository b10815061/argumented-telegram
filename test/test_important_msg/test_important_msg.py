import pytest
from quart import Quart
import json


@pytest.mark.asyncio
async def test_get_important_msg(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    response = await client.get('/channel/important_msg/' + client_id)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_important_msg(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"channel_id": 5206351277, "important_msg_id": 384}
    response = await client.post('/channel/important_msg/' + client_id, json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_important_msg(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"channel_id": 5206351277, "important_msg_id": 384}
    response = await client.delete('/channel/important_msg/' + client_id, json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200
