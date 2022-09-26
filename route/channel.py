from quart import Blueprint, request, websocket
from quart_cors import route_cors
from telethon.sync import TelegramClient
import response
import route.util as utils
import telethon
import json
from telethon import functions, types
import datetime
from DB.crud import priority

blueprint = Blueprint("channel", __name__)


@blueprint.post("/mute")
async def mute():
    """ mute the target channel /
    params(json) :
    [userid: the telegram userID, 
    channel_id : the to-be-muted channelID] 
    -> returns : the channel_id along with the mute state (true = muted)"""
    data = await request.get_json()
    user_id = data["user_id"]
    channel_id = data["channel_id"]
    state = data["state"]
    print(state)
    user = await utils.find_user(utils.client_list, user_id)

    if user != None:
        result = await user(functions.account.UpdateNotifySettingsRequest(
            peer=int(channel_id),
            settings=types.InputPeerNotifySettings(
                show_previews=True,
                silent=False
            )
        ))
        print(result)
        return response.make_response("System", str(channel_id) + str(result))
    else:
        return response.make_response("System", "user not found")

# DEPRECATED
@blueprint.get("/channel/list/<uid>")
async def channel_list(uid):
    user: TelegramClient = await utils.find_user(utils.client_list, int(uid))
    if user == None:
        return response.make_response("System", "user not found / not login", 404)
    
    priority_list = priority.get_channel_prioritys_by_user(uid)
    
    channelList = []
    async for d in user.iter_dialogs():
        channel_pri = -1
        for prioritity in priority_list:
            if (int(prioritity.channel_id) == int(d.entity.id)):
                channel_pri = prioritity.priority
                break
        channel_dto = ChannelDTO(d.entity.id, d.name, channel_pri)
        channelList.append(channel_dto.__dict__)
        # print(f"channel id: {channel_dto.id}, channel name: {channel_dto.name}")
        # channelData = await user.get_entity(d.entity.id)
        # print(d)

    return response.make_response("System", channelList, 200)


class ChannelDTO:
    def __init__(self, channel_id, channel_name, priority):
        self.id = channel_id
        self.name = channel_name
        self.priority = priority