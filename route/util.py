from quart import Websocket
import response
import os
import shutil
import telethon
from typing import Any


def init():

    global client_list, api_hash, api_id
    api_id = 12655046
    api_hash = 'd84ab8008abfb3ec244630d2a6778fc6'
    client_list = dict()

# determine the given phone is valid and return True if client login successfully


async def login(client, phone) -> bool:
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone)
            context = "please enter the code received in your telegram app"
            await websocket.send(response.make_response("system", context))
            code = await websocket.receive()
            await client.sign_in(phone, code)
            return True
        except Exception as e:
            print(e)
            return False
    else:
        return True


async def make_folder(client_id) -> str:  # create user private folder
    path = f'./user/userid{client_id}'
    if not os.path.exists(path):
        os.makedirs(path)
        return ""
    else:
        return response.make_response("system", "Error making folder", 500)


async def delete_folder(client_id) -> str:  # delete user private folder
    path = f"./user/userid{client_id}"
    print(path)
    if not os.path.exists(path):
        return response.make_response("system", "Error deleting folder", 500)
    else:
        shutil.rmtree(path, ignore_errors=True)
        return ""


# find the telethon Client instance
async def find_user(client_list, userID) -> telethon.client:
    userID = int(userID)
    if userID in client_list:
        return client_list[userID]
    else:
        return None
