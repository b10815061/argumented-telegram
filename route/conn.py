from quart import Blueprint, render_template, request, websocket
from asyncio.windows_events import NULL
import os
import telethon
from telethon.sync import TelegramClient
from user.channel.message import incoming_msg
import response

blueprint = Blueprint("connection", __name__)

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


async def make_folder(client_id) -> str:
    path = f'./user/{client_id}'
    if not os.path.exists(path):
        os.makedirs(path)
        return ""
    else:
        return response.make_response("system", "Error making folder", 500)


async def find_user(client_list, userID) -> telethon.client:
    if userID in client_list:
        return client_list[userID]
    else:
        return NULL


@blueprint.route("/disconnect")
async def disconnect():
    userID = request.args.get("user_id")
    user = await find_user(client_list, userID)
    if user != NULL:
        await user.disconnect()
        return response.make_response("system", "log out successfully")
    else:
        return response.make_response("system", "user not found")


@blueprint.websocket("/conn")
async def conn():  # listen on incoming connection
    while True:
        phone = await websocket.receive()
        client = TelegramClient(phone, api_id, api_hash)
        await client.connect()
        if await login(client, phone):
            user = await client.get_me()
            client_list[user.id] = client  # append into client list

            await websocket.send(response.make_response("system", f"Login as {user.id}"))
            # create folder for further usage
            res = await make_folder(user.id)
            if res != "":
                await websocket.send(res)

            # load profile & unread message

            # listen on message
            incoming_msg.listen_on(client_list, user)

            await client.run_until_disconnected()

        else:
            await websocket.send(response.make_response("system", f"login aborted"))