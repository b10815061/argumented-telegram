import base64
from quart import Blueprint, render_template, request, websocket
# from quart_cors import route_cors
from telethon.sync import TelegramClient
from user.channel import message
from user.channel.message import incoming_msg
from quart_jwt_extended import get_jwt_claims, jwt_required
import response
import route.util as utils
import route.DTOs as DTOs
import user.channel.message.util as message_utils
import telethon
import logging
import os
from telethon import functions

blueprint = Blueprint("message", __name__)


@blueprint.post("/sendFile")
# @route_cors(allow_headers=["content-type"],
#             allow_methods=["POST"],
#             allow_origin=["http://localhost:3000"])
@jwt_required
async def sendFile():
    try:
        data: quart.datastruture.FieldStorage = await request.files
        file = data["file"]
        user_id = int(request.args.get("user_id"))
        channel_id = int(request.args.get("channel_id"))

        user_jwt = get_jwt_claims()
        if int(user_id) != int(user_jwt["uid"]):
            return response.make_response("System", "Unauthorized", 401)

        user = await utils.find_user(utils.client_list, user_id)
        if user != None:
            if user.is_connected():
                des = os.path.join(os.getcwd(), "user",
                                   f"userid{user_id}", file.filename)

                await file.save(destination=des)
                with open(des, "rb") as file:
                    file_data = file.read()
                    data = base64.b64encode(file_data).decode()
                file_instance = await user.send_file(channel_id, des)

                os.remove(des)

                # _, sender = await message_utils.get_sender(file_instance, user, channel_instance)

                obj = {
                    "tag": "image",
                    "channel_id": channel_id,
                    "sender_id": user_id,
                    "sender_name": "me",
                    "content": data,
                    "message_id": file_instance.id,  # save the message id for advanced functions
                    "timestamp": str(file_instance.date)
                }

                return response.make_response("image", obj, 200)
            else:
                return response.make_response("System", "You are not Connected!", 400)
        else:
            return response.make_response("System", "user not found", 404)
    except Exception as e:
        logging.error(e)
        return response.make_response("System", "Internal Server Error", 500)


@blueprint.post('/send')
# @route_cors(allow_headers=["content-type"],
#             allow_methods=["POST"],
#             allow_origin=["http://localhost:3000"])
@jwt_required
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

    user_jwt = get_jwt_claims()
    if int(user_id) != int(user_jwt["uid"]):
        return response.make_response("System", "Unauthorized", 401)

    user = await utils.find_user(utils.client_list, user_id)

    if user != None:
        if user.is_connected():
            try:
                name = await user.get_entity(int(channel_id))
                message_instance = await user.send_message(entity=name, message=message)
                obj = {
                    "tag": "message",
                    "channel_id": channel_id,
                    "sender_id": user_id,
                    "sender_name": "me",
                    "content": message,
                    "message_id": message_instance.id,  # save the message id for advanced functions
                    "timestamp": str(message_instance.date)
                }
                return response.make_response("message", obj, 200)
            except Exception as e:
                logging.error(e)
                return response.make_response("System", f'you can\'t write in this channel ({channel_id})', 401)
        else:

            return response.make_response("System", "You are not Connected!", 400)
    else:
        return response.make_response("System", "user not found", 404)


@blueprint.get("/getPinnedMessage")
@jwt_required
async def getPin():
    """
    due to the API of telethon
    currently support only 1 pinned message
    """
    try:
        user_id = int(request.args.get("user_id"))
        channel_id = int(request.args.get("channel_id"))

        user_jwt = get_jwt_claims()
        if int(user_id) != int(user_jwt["uid"]):
            return response.make_response("System", "Unauthorized", 401)

        user = await utils.find_user(utils.client_list, user_id)
        if user != None:
            if user.is_connected():
                channel_instance = await user.get_entity(channel_id)
                if type(channel_instance) == telethon.tl.types.User:
                    fulluser = await user(
                        functions.users.GetFullUserRequest(id=channel_id))
                    try:
                        pinned_message_ids = fulluser.full_user.pinned_msg_id
                    except:
                        pinned_message_ids = fulluser.pinned_msg_id
                elif type(channel_instance) == telethon.tl.types.Chat:
                    fulluser = await user(
                        functions.messages.GetFullChatRequest(chat_id=channel_id))
                    pinned_message_ids = fulluser.full_chat.pinned_msg_id
                else:
                    fulluser = await user(
                        functions.channels.GetFullChannelRequest(channel=channel_id))
                    pinned_message_ids = fulluser.full_chat.pinned_msg_id
                if pinned_message_ids != None:
                    pinned_message = await user.get_messages(
                        channel_id, ids=pinned_message_ids)
                    _, context = await message_utils.outline_context_handler(pinned_message)
                else:
                    pinned_message_ids = -1
                    context = ""
                obj = {
                    "message_id": pinned_message_ids,
                    "context": context
                }
                return response.make_response("sys", obj, 200)
        else:
            return response.make_response("sys", "not login", 401)
    except Exception as e:
        logging.error(e)
        return response.make_response("err", e, 500)


@ blueprint.post("/pin")
@jwt_required
async def pin():
    """pin a messaage in the channel /
    params(json) : [user_id : the telegram userID,
    channel_id : the telegram channelID,
    message_id : the to-be-pinned messageID]
    """
    try:
        data = await request.get_json()
        user_id = int(data["user_id"])
        channel_id = int(data["channel_id"])
        message_id = int(data["message_id"])

        user_jwt = get_jwt_claims()
        if int(user_id) != int(user_jwt["uid"]):
            return response.make_response("System", "Unauthorized", 401)

        user = await utils.find_user(utils.client_list, user_id)
        if user != None:
            if user.is_connected():
                try:
                    name = await user.get_entity(channel_id)
                    await user.pin_message(entity=name, message=message_id)
                    return response.make_response("System", f'{channel_id} : {message_id}', 200)
                except Exception as e:
                    logging.error(e)
                    return response.make_response("System", f'you can\'t pin in this channel ({channel_id})', 401)
            else:

                return response.make_response("System", "You are not Connected!", 400)
        else:
            return response.make_response("System", "user not found", 404)
    except Exception as e:
        return response.make_response("Error", e, 500)


@ blueprint.post("/ack")
@jwt_required
async def ack():
    """ read a given channel message /
    params(json) : [
    userid : the telegram userID,
    channel_id : the target channel to ack all unread messages]
    """
    data = await request.get_json()
    user_id = data["user_id"]
    user_jwt = get_jwt_claims()
    if int(user_id) != int(user_jwt["uid"]):
        return response.make_response("System", "Unauthorized", 401)

    user = await utils.find_user(utils.client_list, user_id)
    try:
        if user != None:
            if user.is_connected():
                channel_id = data["channel_id"]
                await user.send_read_acknowledge(channel_id)
                obj = {
                    "channel_id": channel_id
                }
                return response.make_response("System", obj, 200)
            else:
                return response.make_response("System", "You are not connected!", 400)
        else:
            return response.make_response("System", "user not found", 404)
    except Exception as e:
        logging.error(e)
        return response.make_response("System", e, 500)


@blueprint.delete("/deleteMessage")
@jwt_required
async def deleteMessage():
    try:
        user_id = int(request.args.get("user_id"))
        channel_id = int(request.args.get("channel_id"))
        message_id = int(request.args.get("message_id"))

        user_jwt = get_jwt_claims()
        if int(user_id) != int(user_jwt["uid"]):
            return response.make_response("System", "Unauthorized", 401)

        user = await utils.find_user(utils.client_list, user_id)
        await user.delete_messages(entity=channel_id, message_ids=message_id)
        return response.make_response("System", "OK", 200)
    except Exception as e:
        logging.error(e)
        return response.make_response("Error", e, 400)


@blueprint.get('/getMessage')
@jwt_required
async def getMessage():
    user_id = int(request.args.get("user_id"))
    channel_id = int(request.args.get("channel_id"))
    message_id = int(request.args.get("message_id"))

    user_jwt = get_jwt_claims()
    if int(user_id) != int(user_jwt["uid"]):
        return response.make_response("System", "Unauthorized", 401)

    user = await utils.find_user(utils.client_list, user_id)

    if user != None:
        if user.is_connected():
            channel_id: int = int(channel_id)
            from_message_id: int = 0 if int(
                message_id) == 0 else int(message_id)
            try:
                channel_instance: telethon.Channel = await user.get_entity((int(channel_id)))
                msgs: list[telethon.message] = await user.get_messages(channel_instance, limit=1, offset_id=from_message_id)
                context = []

                msg_instance: telethon.message
                for msg_instance in msgs:
                    sender_id, sender = await message_utils.get_sender(msg_instance, user, channel_instance)
                    # get the message content
                    try:
                        tag, msg_content = await message_utils.context_handler(
                            user_id, user, msg_instance)
                    except Exception as e:
                        logging.error(e)
                        logging.error(msg_instance)
                        logging.error(msg_content)
                        raise Exception(e)

                    # get the time when the message has been sent
                    msg_time = msg_instance.date
                    if (sender_id is None):
                        sender_id = channel_id

                    obj = DTOs.MessageDTO(sender_id=sender_id, sender_name=sender, channel_id=channel_id,
                                          message_id=msg_instance.id, content=msg_content, timestamp=str(msg_time), tag=tag)

                    # obj = {
                    #     "tag": tag,
                    #     "channel": channel_id,
                    #     "from": sender,
                    #     "sender_id": sender_id,
                    #     "data": msg_content,
                    #     "message_id": msg_instance.id,  # save the message id for advanced functions
                    #     "timestamp": str(msg_time)
                    # }
                    context.append(obj.__dict__)

                message = response.make_response("message", context, 200)
            except Exception as e:
                logging.error(e)
                err_msg = {
                    "className": e.__class__.__name__,
                    "message": e.__str__()
                }
                message = response.make_response("Error", err_msg, 500)
                logging.error("channel_not_found")
        else:
            message = response.make_response(
                "Error", "you are not connected", 400)
    return message


"""
job:    get message list with specific target
route:  GET "/messages"
input:  user_id: user id, channel_id: channel id, message_id: message id, limit: length of message list to get (may be less if reaches the newest one) (default 10), reverse (1 or 0): whether getting older or newer data (1 = newer) (default True)
output: json format message data list, 200
"""


@blueprint.get('/messages')
@jwt_required
async def getMessageList():
    user_id = request.args.get("user_id")
    channel_id = request.args.get("channel_id")
    message_id = request.args.get("message_id")
    limit = request.args.get("limit")
    reverse = request.args.get("reverse")

    if user_id == None:
        return response.make_response("System", "userid not provided", 404)

    if channel_id == None:
        return response.make_response("System", "channelid not provided", 404)

    if message_id == None:
        return response.make_response("System", "messageid not provided", 404)

    user_jwt = get_jwt_claims()
    if int(user_id) != int(user_jwt["uid"]):
        return response.make_response("System", "Unauthorized", 401)

    user = await utils.find_user(utils.client_list, user_id)
    if user == None:
        return response.make_response("System", "user not found / not login", 404)

    if limit == None:
        limit = 10

    if reverse == None:
        reverse = True

    user_id = int(user_id)
    channel_id = int(channel_id)
    reverse = int(reverse) == 1
    limit = int(limit)

    channel_instance = await user.get_entity(channel_id)
    message_list = []
    msgs = []
    if limit == -1:
        msgs = await user.get_messages(channel_instance, limit=None, offset_id=int(message_id) - 1, reverse=True)
    else:
        # +-1 is to contact with telethon API, which is exclusive
        if reverse:
            message_id = int(message_id) - 1
        else:
            message_id = int(message_id) + 1
        msgs = await user.get_messages(channel_instance, limit=limit, offset_id=message_id, reverse=reverse)

    for msg_instance in msgs:  # totally same as what's in getMessage, which is quite wired
        sender_id, sender = await message_utils.get_sender(msg_instance, user, channel_instance)
        # get the message content
        try:
            tag, msg_content = await message_utils.context_handler(
                user_id, user, msg_instance)
        except Exception as e:
            logging.error(e)
            logging.error(msg_instance)
            logging.error(msg_content)
            raise Exception(e)

        # get the time when the message has been sent
        msg_time = msg_instance.date
        if (sender_id is None):
            sender_id = channel_id

        obj = DTOs.MessageDTO(sender_id=sender_id, sender_name=sender, channel_id=channel_id,
                              message_id=msg_instance.id, content=msg_content, timestamp=str(msg_time), tag=tag)

        # obj = {
        #     "tag": tag,
        #     "channel": channel_id,
        #     "from": sender,
        #     "sender_id": sender_id,
        #     "data": msg_content,
        #     "message_id": msg_instance.id,  # save the message id for advanced functions
        #     "timestamp": str(msg_time)
        # }
        message_list.append(obj.__dict__)

    message_list = sorted(message_list, key=lambda d: d['message_id'])
    return response.make_response("message", message_list, 200)
