from quart import Blueprint, render_template, request # , websocket
from telethon.sync import TelegramClient
from user.channel.message import incoming_msg
import response
import route.util as utils
import telethon
import json
import route.util as utils

blueprint = Blueprint("sendMessage", __name__)


# @blueprint.websocket('/ws')
@utils.sio.event
async def ws(data):
    pair = json.loads(data)
    user = (pair["user_id"])
    global client_list
    user = await utils.find_user(utils.client_list, user)
    if user != None:
        if user.is_connected():
            try:
                id = pair["channel"]
                name = await user.get_entity(int(id))
                print(name)
                await user.send_message(entity=name, message=pair["message"])
                await utils.sio.send(f'{pair["channel"]} : {pair["message"]}') # websocket.send(f'{pair["channel"]} : {pair["message"]}')
                print("message sent")
            except:
                await utils.sio.send(f'you can\'t write in this channel ({pair["channel"]})') # websocket.send(f'you can\'t write in this channel ({pair["channel"]})')
        else:
            await utils.sio.send("System : You are not Connected!") # websocket.send("System : You are not Connected!")
    else:
        await utils.sio.send("System : user not found") # websocket.send("System : user not found")
