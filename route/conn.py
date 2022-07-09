from quart import Blueprint, render_template, request, websocket
from telethon.sync import TelegramClient
from user.channel.message import incoming_msg
import response
import route.util as utils

blueprint = Blueprint("connection", __name__)


@blueprint.route("/disconnect")
async def disconnect():
    userID: str = (request.args.get("user_id"))
    user = await utils.find_user(utils.client_list, userID)
    if user != None:
        res = await utils.delete_folder(userID)
        if res != "":
            return res
        await user.disconnect()
        return response.make_response("system", "log out successfully")
    else:
        return response.make_response("system", "user not found")


@blueprint.websocket("/conn")
async def conn():  # listen on incoming connection
    while True:
        phone = await websocket.receive()
        client = TelegramClient(phone, utils.api_id, utils.api_hash)
        await client.connect()
        if await utils.login(client, phone):
            user = await client.get_me()
            # append into client list !!! todo -> might want to use token instead

            await websocket.send(response.make_response("system", f"Login as {user.id}"))
            # create folder for further usage
            res = await utils.make_folder(user.id)
            if res != "":
                await websocket.send(res)

            utils.client_list[user.id] = client

            # load profile

            # send unread message count

            # listen on message
            incoming_msg.listen_on(utils.client_list, user)

            await client.run_until_disconnected()

        else:
            await websocket.send(response.make_response("system", f"login aborted"))
