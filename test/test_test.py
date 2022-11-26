import pytest
from quart import Quart


# @pytest.mark.asyncio
# async def test_app(quart_app: Quart):
#     client = quart_app.test_client()
#     cid = 1910045535
#     response = await client.get('/setting/privacy/' + str(cid))
#     print(response)
#     result = await response.get_json()
#     print(result)
#     result = await response.get_data()
#     print(result)
#     assert response.status_code == 200

@pytest.mark.asyncio
async def test_post_priority(quart_app: Quart, client_id):
    client = quart_app.test_client()
    data = {"phone": "+8860909855200"}
    print(client_id)
    response = await client.post('/login', json=data)
    print(response)
    result = await response.get_json()
    print(result)
    result = await response.get_data()
    print(result)
    assert response.status_code == 202