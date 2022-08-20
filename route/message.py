from quart import Blueprint, render_template, request, websocket
from quart_cors import route_cors
from telethon.sync import TelegramClient
from user.channel.message import incoming_msg
import response
import route.util as utils
import telethon
import json
import os
from pprint import pprint

blueprint = Blueprint("message", __name__)


@blueprint.post("/sendFile")
@route_cors(allow_headers=["content-type"],
            allow_methods=["POST"],
            allow_origin=["http://localhost:3000"])
async def sendFile():
    try:
        data: quart.datastruture.FieldStorage = await request.files
        print(data)
        file = data["file"]
        print(file)
        user_id = int(request.args.get("user_id"))
        channel_id = int(request.args.get("channel_id"))
        print(user_id, channel_id)
        user = utils.find_user(utils.client_list, user_id)
        if user != None:
            if user.is_connected():
                des = os.path.join(os.getcwd(), "user",
                                   f"userid{user_id}", file.filename)

                await file.save(destination=des)
                await user.send_file(channel_id, des)

                os.remove(des)
                return response.make_response("System", f"{file.filename} sent")
            else:
                return response.make_response("System", "You are not Connected!")
        else:
            return response.make_response("System", "user not found")
    except Exception as e:
        print(e)
        return response.make_response("System", "Internal Server Error", 500)


@blueprint.post('/send')
@route_cors(allow_headers=["content-type"],
            allow_methods=["POST"],
            allow_origin=["http://localhost:3000"])
async def send():
    """send a message to the given channel /
    params(json) : [user_id : the teletgram userID,
    channel_id : the telegram channelID,
    message : message to be sent]
    """
    data = await request.get_json()
    user_id = data["user_id"]
    channel_id = data["channel_id"]
    message = data["message"]
    user = utils.find_user(utils.client_list, user_id)

    if user != None:
        if user.is_connected():
            try:
                name = await user.get_entity(int(channel_id))
                await user.send_message(entity=name, message=message)
                return response.make_response("System", f'{channel_id} : {message}')
            except Exception as e:
                print(e)
                return response.make_response("System", f'you can\'t write in this channel ({channel_id})')
        else:

            return response.make_response("System", "You are not Connected!", 400)
    else:
        return response.make_response("System", "user not found", 400)


@ blueprint.post("/pin")
async def pin():
    """pin a messaage in the channel /
    params(json) : [user_id : the telegram userID,
    channel_id : the telegram channelID,
    message_id : the to-be-pinned messageID]
    """
    data = await request.get_json()
    user_id = data["user_id"]
    channel_id = data["channel_id"]
    message_id: str = data["message_id"]
    user = utils.find_user(utils.client_list, user_id)
    if user != None:
        if user.is_connected():
            try:
                name = await user.get_entity(int(channel_id))
                await user.pin_message(entity=name, message=int(message_id))
                return response.make_response("System", f'{channel_id} : {message_id}')
            except Exception as e:
                print(e)
                return response.make_response("System", f'you can\'t pin in this channel ({channel_id})')
        else:

            return response.make_response("System", "You are not Connected!")
    else:
        return response.make_response("System", "user not found")


@ blueprint.post("/ack")
async def ack():
    """ read a given channel message /
    params(json) : [
    userid : the telegram userID,
    channel_id : the target channel to ack all unread messages]
    """
    data = await request.get_json()
    user_id = data["user_id"]
    user = utils.find_user(utils.client_list, user_id)
    if user != None:
        if user.is_connect():
            channel_id = data["channel_id"]
            await user.send_read_acknowledge(channel_id)
        else:
            return response.make_response("System", "You are not connected!")
    else:
        return response.make_response("System", "user not found")
