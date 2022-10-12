from quart import Blueprint, Request, ResponseReturnValue, request
from DB.crud import important_msg as Important_Msg
from telethon import TelegramClient
from telethon.tl.types import Message
import route.DTOs as DTOs
import route.util as utils
import user.channel.message.util as message_utils
import response

blueprint = Blueprint("important_msg", __name__)

"""
job:    get channel important_msgs in a channel
route:  GET "/channel/important_msg/<id>"
input:  channel_id: channel id (parameter) (optional)
output: list of important messages, 200
"""


@blueprint.get("/channel/important_msg/<id>")
async def getImportantMsg(id):
    channel_id = request.args.get("channel_id")
    user: TelegramClient = await utils.find_user(utils.client_list, int(id))
    if user == None:
        return response.make_response("System", "user not found / not login", 404)

    important_msg_list = []

    if (channel_id == None):
        important_msg_list = Important_Msg.get_channel_important_msgs_by_user(
            id)
    else:
        important_msg_list = Important_Msg.get_channel_important_msgs(
            id, str(channel_id))
    output_msg_list = []
    for important_msg in important_msg_list:
        channel_instance = await user.get_entity((int(important_msg.channel_id)))

        msg_instance: Message = await user.get_messages(channel_instance, ids=int(important_msg.important_msg_id))
        if msg_instance != None:
            sender_id, sender_name = await message_utils.get_sender(msg_instance, user, channel_instance)
            # get the message content
            try:
                tag, msg_content = await message_utils.context_handler(
                    id, user, msg_instance)
            except Exception as e:
                print(e)
                print(msg_instance)
                print(msg_content)
                raise Exception(e)

            # get the time when the message has been sent
            msg_time = msg_instance.date
            if (sender_id is None):
                sender_id = important_msg.channel_id

            output_msg_list.append(DTOs.MessageDTO(sender_id=sender_id, sender_name=sender_name, channel_id=important_msg.channel_id,
                                   message_id=important_msg.important_msg_id, content=msg_content, timestamp=str(msg_time), tag=tag).__dict__)

    return response.make_response("System", output_msg_list, 200)

"""
job:    add channel important_msg
route:  POST "/channel/important_msg/<id>"
input:  channel_id: channel id, important_msg_id: message id to be important (json)
output: OK, 200
"""


@blueprint.post("/channel/important_msg/<id>")
async def setImportantMsg(id):
    data = await request.get_json()

    if not ("channel_id" in data):
        return response.make_response("System", "lack of channel_id", 400)
    if not ("important_msg_id" in data):
        return response.make_response("System", "lack of important_msg_id", 400)

    user: TelegramClient = await utils.find_user(utils.client_list, int(id))
    if user == None:
        return response.make_response("System", "user not found / not login", 404)

    channel_instance = await user.get_entity((int(data["channel_id"])))
    if channel_instance == None:
        return response.make_response("System", "channel not exist", 404)
    msg_instance: Message = await user.get_messages(channel_instance, ids=int(data["important_msg_id"]))
    if msg_instance == None:
        return response.make_response("System", "message not exist", 404)

    new_important_msg = Important_Msg.create_channel_important_msg(
        id, str(data["channel_id"]), str(data["important_msg_id"]))

    if new_important_msg == None:
        return response.make_response("System", "important_msg add failed", 500)
    return response.make_response("System", "OK", 200)

"""
job:    delete channel important_msg
route:  DELETE "/channel/important_msg/<id>"
input:  channel_id: channel id, important_msg_id: message id to be important (json)
output: OK, 200
"""


@blueprint.delete("/channel/important_msg/<id>")
async def deleteImportantMsg(id):
    data = await request.get_json()

    if not ("channel_id" in data):
        return response.make_response("System", "lack of channel_id", 400)
    if not ("important_msg_id" in data):
        return response.make_response("System", "lack of important_msg_id", 400)

    delete_important_msg_result = Important_Msg.delete_channel_important_msg(
        id, str(data["channel_id"]), str(data["important_msg_id"]))

    if delete_important_msg_result == False:
        return response.make_response("System", "important_msg delete failed", 500)
    return response.make_response("System", "OK", 200)
