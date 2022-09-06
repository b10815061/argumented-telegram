from quart import Blueprint, render_template, request, websocket
# from quart_cors import route_cors
from telethon.sync import TelegramClient
from user.channel.message import incoming_msg
import response
import route.util as utils
import user.channel.message.util as message_utils
import telethon
import json
import os
from pprint import pprint

blueprint = Blueprint("message", __name__)


@blueprint.post("/sendFile")
# @route_cors(allow_headers=["content-type"],
#             allow_methods=["POST"],
#             allow_origin=["http://localhost:3000"])
async def sendFile():
    try:
        data: quart.datastruture.FieldStorage = await request.files
        print(data)
        file = data["file"]
        print(file)
        user_id = int(request.args.get("user_id"))
        channel_id = int(request.args.get("channel_id"))
        print(user_id, channel_id)
        user = await utils.find_user(utils.client_list, user_id)
        if user != None:
            if user.is_connected():
                des = os.path.join(os.getcwd(), "user",
                                   f"userid{user_id}", file.filename)

                await file.save(destination=des)
                await user.send_file(channel_id, des)

                os.remove(des)
                return response.make_response("System", f"{file.filename} sent", 200)
            else:
                return response.make_response("System", "You are not Connected!", 400)
        else:
            return response.make_response("System", "user not found", 404)
    except Exception as e:
        print(e)
        return response.make_response("System", "Internal Server Error", 500)


@blueprint.post('/send')
# @route_cors(allow_headers=["content-type"],
#             allow_methods=["POST"],
#             allow_origin=["http://localhost:3000"])
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
    user = await utils.find_user(utils.client_list, user_id)

    if user != None:
        if user.is_connected():
            try:
                name = await user.get_entity(int(channel_id))
                await user.send_message(entity=name, message=message)
                return response.make_response("System", f'{channel_id} : {message}', 200)
            except Exception as e:
                print(e)
                return response.make_response("System", f'you can\'t write in this channel ({channel_id})', 401)
        else:

            return response.make_response("System", "You are not Connected!", 400)
    else:
        return response.make_response("System", "user not found", 404)


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
    user = await utils.find_user(utils.client_list, user_id)
    if user != None:
        if user.is_connected():
            try:
                name = await user.get_entity(int(channel_id))
                await user.pin_message(entity=name, message=int(message_id))
                return response.make_response("System", f'{channel_id} : {message_id}', 200)
            except Exception as e:
                print(e)
                return response.make_response("System", f'you can\'t pin in this channel ({channel_id})', 401)
        else:

            return response.make_response("System", "You are not Connected!", 400)
    else:
        return response.make_response("System", "user not found", 404)


@ blueprint.post("/ack")
async def ack():
    """ read a given channel message /
    params(json) : [
    userid : the telegram userID,
    channel_id : the target channel to ack all unread messages]
    """
    data = await request.get_json()
    user_id = data["user_id"]
    user = await utils.find_user(utils.client_list, user_id)
    if user != None:
        if user.is_connect():
            channel_id = data["channel_id"]
            await user.send_read_acknowledge(channel_id)
        else:
            return response.make_response("System", "You are not connected!", 400)
    else:
        return response.make_response("System", "user not found", 404)


@blueprint.get('/getMessage')
async def getMessage():
    user_id = int(request.args.get("user_id"))
    channel_id = int(request.args.get("channel_id"))
    message_id = int(request.args.get("message_id"))
    user = await utils.find_user(utils.client_list, user_id)

    if user != None:
        if user.is_connected():
            channel_id: int = int(channel_id)
            from_message_id: int = 0 if int(
                message_id) == 0 else int(message_id)
            try:
                channel_instance: telethon.Channel = await user.get_entity((int(channel_id)))
                msgs: list[telethon.message] = await user.get_messages(channel_instance, limit=5, offset_id=from_message_id)
                context = []

                msg_instance: telethon.message
                for msg_instance in msgs:
                    # get the sender of the msg
                    try:
                        # !!! messages in Chat (2 frineds channel) has no from_id attribute
                        if(msg_instance.from_id != None):
                            sender_instance = await user.get_entity(msg_instance.from_id.user_id)
                        else:
                            # which menas if the from_id is NoneType, then the channel itself is a user
                            sender_instance = channel_instance
                        try:
                            if sender_instance.username != None:
                                sender = sender_instance.username
                            elif sender_instance.first_name != None:
                                lname = sender_instance.last_name if sender_instance.last_name != None else ""
                                sender = sender_instance.first_name + lname
                            else:
                                print("AN ERROR MIGHT OCCUR")
                                print(sender_instance, end="\n\n\n")
                        except:
                            sender = sender_instance.title
                    except Exception as e:
                        print(e)
                        print(channel_instance)
                        print(msgs[0])
                    # get the message content
                    try:
                        tag, msg_content = await message_utils.context_handler(
                            user_id, user, msg_instance)
                    except Exception as e:
                        print(e)
                        print(msg_instance)
                        print(msg_content)

                    # get the time when the message has been sent
                    msg_time = msg_instance.date

                    obj = {
                        "tag": tag,
                        "channel": channel_id,
                        "from": sender,
                        "data": msg_content,
                        "message_id": msg_instance.id,  # save the message id for advanced functions
                        "timestamp": str(msg_time)
                    }
                    context.append(obj)

                message = response.make_response("message", context, 200)
            except Exception as e:
                print(e)
                message = response.make_response("Error", e, 500)
                print("channel_not_found")
        else:
            message = response.make_response(
                "Error", "you are not connected", 400)
    return message
