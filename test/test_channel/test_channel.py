import pytest
from quart import Quart
import json


@pytest.mark.asyncio
async def test_post_mute(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"user_id": client_id, "channel_id": 777000, "state": False}
    response = await client.post('/mute', json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_cahnnel_list(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    response = await client.get('/channel/list/' + client_id + '?is_basic=true')
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result['context'][0])
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_photo_list(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    response = await client.get('/channel/photo/' + client_id + '?user_list=777000')
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result['context'][0])
    assert response.status_code == 200
