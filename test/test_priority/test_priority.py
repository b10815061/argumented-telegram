import pytest
from quart import Quart
import json


@pytest.mark.asyncio
async def test_post_priority(quart_app: Quart, client_id: str):
    client = quart_app.test_client()

    data = {"channel_id": 5206351277, "priority": 1}
    response = await client.post('/channel/priority/' + client_id, json=data)
    print(response)
    result = await response.get_data()
    result = json.loads(result.decode('utf-8'))
    print(result)
    assert response.status_code == 200
