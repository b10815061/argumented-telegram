from quart import Blueprint, Request, ResponseReturnValue, request
from DB.crud import priority
import route.util as utils
import response

blueprint = Blueprint("priority", __name__)

"""
job:    update channel priority
route:  POST "/channel/priority/<id>"
input:  channel_id: channel id, priority: priority value (json)
output: stringify setting situation, 200
"""


@blueprint.post("/channel/priority/<id>")
async def updatePriority(id):
    data = await request.get_json()

    if not ("channel_id" in data):
        return response.make_response("System", "lack of channel_id", 400)
    if not ("priority" in data):
        return response.make_response("System", "lack of priority", 400)

    new_priority = priority.create_channel_priority(
        id, data["channel_id"], data["priority"])

    if new_priority == None:
        return response.make_response("System", "priority set failed", 500)
    # print(new_priority.__dict__)
    return response.make_response("System", "OK", 200)
