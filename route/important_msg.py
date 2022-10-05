from quart import Blueprint, Request, ResponseReturnValue, request
from DB.crud import important_msg as Important_Msg
import route.util as utils
import response

blueprint = Blueprint("important_msg", __name__)


class ImportantMsgDTO:
    def __init__(self, user_id, channel_id, important_msg_id):
        self.user_id = user_id
        self.channel_id = channel_id
        self.important_msg_id = important_msg_id


"""
job:    get channel important_msgs in a channel
route:  GET "/channel/important_msg/<id>"
input:  channel_id: channel id (parameter) (optional)
output: list of important messages, 200
"""


@blueprint.get("/channel/important_msg/<id>")
async def getImportantMsg(id):
    channel_id = request.args.get("channel_id")

    important_msg_list = []

    if (channel_id == None):
        important_msg_list = Important_Msg.get_channel_important_msgs_by_user(
            id)
    else:
        important_msg_list = Important_Msg.get_channel_important_msgs(
            id, str(channel_id))
    for idx, important_msg in enumerate(important_msg_list):
        important_msg_list[idx] = ImportantMsgDTO(
            important_msg.user_id, important_msg.channel_id, important_msg.important_msg_id).__dict__

    return response.make_response("System", important_msg_list, 200)

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
