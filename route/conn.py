from pydoc import cli
from quart import Blueprint, render_template, request, websocket
from telethon.sync import TelegramClient
from user.channel.message import incoming_msg, util
import response
import route.util as utils
import telethon

blueprint = Blueprint("connection", __name__)


@blueprint.route("/disconnect")
async def disconnect():
    userID: str = (request.args.get("user_id"))
    user = utils.find_user(utils.client_list, userID)
    if user != None:
        res = await utils.delete_folder(userID)
        if res != "":
            return res
        await user.disconnect()
        return response.make_response("system", "log out successfully")
    else:
        return response.make_response("system", "user not found")


@blueprint.websocket("/a")
async def a():  # listen on incoming connection
    while True:
        phone = await websocket.receive()
        client = TelegramClient(phone, utils.api_id, utils.api_hash)
        await client.connect()
        if await utils.has_session(client, phone):
            user: telethon.client_describe_obj = await client.get_me()
            # append into client list !!! todo -> might want to use token instead

            await websocket.send(response.make_response("system", f"Login as {user.id}"))
            # create folder for further usage
            res = await utils.make_folder(user.id)
            if res != "":
                await websocket.send(res)

            utils.client_list[user.id] = client

            dialogs: list[telethon.Dialog] = await client.get_dialogs()
            # load profile
            # await utils.send_profile(dialogs, client, user.id)
            # send unread message count
            await utils.send_unread_count(dialogs)
            # listen on message
            incoming_msg.listen_on(utils.client_list, user)

            await client.run_until_disconnected()

        else:
            await websocket.send(response.make_response("system", f"login aborted"))


@blueprint.post("/login")
async def login() -> str:  # return userID to frontend
    data = await request.get_json()
    phone = data["phone"]
    client = TelegramClient(phone, utils.api_id, utils.api_hash)
    await client.connect()
    if await utils.has_session(client, phone):
        me = await client.get_me()
        utils.client_list[me.id] = client
        return response.make_response("system", f"Login as {me.id}")
    else:
        return response.make_response("system", "please enter the code received in your telegram app")


@blueprint.websocket("/conn")
async def conn():
    while True:
        userid = await websocket.receive()
        client = utils.find_user(utils.client_list, userid)
        user: telethon.client_describe_obj = await client.get_me()

        res = await utils.make_folder(user.id)
        if res != "":
            await websocket.send(res)

        utils.client_list[user.id] = client

        dialogs: list[telethon.Dialog] = await client.get_dialogs()
        # load profile
        # await utils.send_profile(dialogs, client, user.id)
        # send unread message count
        await utils.send_unread_count(dialogs)
        # listen on message
        incoming_msg.listen_on(utils.client_list, user)
