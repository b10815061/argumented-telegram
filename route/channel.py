from quart import Blueprint, request, websocket
from quart_cors import route_cors
from telethon.sync import TelegramClient
import response
import route.util as utils
from telethon import functions, types
from DB.crud import priority
from telethon.sync import TelegramClient
from PIL import Image
import io
import base64

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


"""
job:    get update phone code request
route:  GET "/channel/list/<uid>"
input:  slice_by: how many messages count as 1 page (default 10), page_count: # of page (if not provided, return all), is_basic: if it returns only basic content or not (default false) (optional)
output: channel_list: each object contains id, name, priority, b64, unread_count
note:   it may be slow because of lots of image request
"""


@blueprint.get("/channel/list/<uid>")
async def channel_list(uid):
    user: TelegramClient = await utils.find_user(utils.client_list, int(uid))
    if user == None:
        return response.make_response("System", "user not found / not login", 404)

    slice_by = request.args.get("slice_by")
    page_count = request.args.get("page_count")
    is_basic = request.args.get("is_basic")

    if slice_by == None:
        slice_by = 10
    else:
        slice_by = int(slice_by)

    if page_count == None:
        page_count = -1
    else:
        page_count = int(page_count)

    is_basic = ((is_basic != None) and (
        is_basic == "True" or is_basic == "true"))

    priority_list = priority.get_channel_prioritys_by_user(uid)

    channelList = []
    channel_count = 0
    async for d in user.iter_dialogs():
        channel_pri = -1
        for prioritity in priority_list:
            if (int(prioritity.channel_id) == int(d.entity.id)):
                channel_pri = prioritity.priority
                break

        b64 = ""
        if not is_basic and (page_count == -1 or (page_count != -1 and channel_count >= slice_by * page_count and channel_count >= slice_by * (page_count + 1))):
            profile_result = await user.download_profile_photo(d, file=bytes)

            if profile_result != None:
                # tmp_image = Image.open(io.BytesIO(profile_result))
                # tmp_image.thumbnail([64, 64], Image.ANTIALIAS)
                buf = io.BytesIO(profile_result)
                # tmp_image.save(buf, format="png")
                byte_thumb = buf.getvalue()
                b64 = base64.b64encode(byte_thumb)
                b64 = b64.decode()

        channel_dto = ChannelDTO(
            d.entity.id, d.name, channel_pri, b64, d.unread_count)
        channelList.append(channel_dto.__dict__)
        # print(f"channel id: {channel_dto.id}, channel name: {channel_dto.name}")
        # channelData = await user.get_entity(d.entity.id)
        # print(d)
        channel_count += 1

    if page_count != -1:
        channelList = channelList[page_count * slice_by: (page_count + 1) * slice_by]
    return response.make_response("System", channelList, 200)


class ChannelDTO:
    def __init__(self, channel_id, channel_name, priority, b64, unread_count):
        self.id = channel_id
        self.name = channel_name
        self.priority = priority
        self.b64 = b64
        self.unread_count = unread_count
