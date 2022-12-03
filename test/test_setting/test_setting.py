import pytest
from quart import Quart
import json

# not tested in setting: POST "/setting/photo/<id>", POST "/setting/phone/code/<id>", POST "/setting/phone/varify/<id>"


@pytest.mark.asyncio
async def test_get_privacy(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    response = await client.get('/setting/privacy/' + client_id)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_privacy(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"Forwards": 1, "ProfilePhoto": 1}
    response = await client.post('/setting/privacy/' + client_id, json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_profile(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"about": "ouob"}
    response = await client.post('/setting/profile/' + client_id, json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_username(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"name": "tonatfish"}
    response = await client.post('/setting/username/' + client_id, json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    # not change or successful change
    assert response.status_code == 200 or result["context"]["className"] == "UsernameNotModifiedError"


@pytest.mark.asyncio
async def test_get_ui(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    response = await client.get('/setting/ui/' + client_id)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_ui(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"font_size": 1, "language": "en"}
    response = await client.patch('/setting/ui/' + client_id, json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200
