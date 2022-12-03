import pytest
from quart import Quart
import json

# not tested in message: /sendFile


@pytest.mark.asyncio
async def test_post_send(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"user_id": client_id, "channel_id": "777000", "message": "test"}
    response = await client.post('/send', json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_pinned_message(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    response = await client.get('/getPinnedMessage?user_id=' + client_id + '&channel_id=777000')
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_pin(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"user_id": client_id, "channel_id": 777000, "message_id": 364}
    response = await client.post('/pin', json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_ack(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"user_id": client_id, "channel_id": 777000}
    response = await client.post('/ack', json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_important_msg(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"user_id": client_id, "channel_id": 777000, "message_id": 365}
    response = await client.delete('/deleteMessage?user_id=' + client_id + '&channel_id=777000&message_id=365', json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_message(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    response = await client.get('/getMessage?user_id=' + client_id + '&channel_id=777000&message_id=364')
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_messages(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    response = await client.get('/messages?user_id=' + client_id + '&channel_id=777000&message_id=364&limit=10')
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200
