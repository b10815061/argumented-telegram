from quart import Blueprint, request, websocket
from quart_cors import route_cors
from telethon.sync import TelegramClient
from quart_jwt_extended import get_jwt_claims, jwt_required
import response
import route.util as utils
from telethon import functions, types
from DB.crud import priority
import telethon.tl.custom.dialog
import route.DTOs as DTOs
from PIL import Image
import io
import base64
import redis_instance

blueprint = Blueprint("channel", __name__)


@blueprint.post("/mute")
@jwt_required
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

    user_jwt = get_jwt_claims()
    if int(user_id) != int(user_jwt["uid"]):
        return response.make_response("System", "Unauthorized", 401)

    user = await utils.find_user(utils.client_list, user_id)

    if user != None:
        result = await user(functions.account.UpdateNotifySettingsRequest(
            peer=int(channel_id),
            settings=types.InputPeerNotifySettings(
                show_previews=True,
                silent=False
            )
        ))
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
@jwt_required
async def channel_list(uid):
    user_jwt = get_jwt_claims()
    if int(uid) != int(user_jwt["uid"]):
        return response.make_response("System", "Unauthorized", 401)

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

    # redis_key = "/channel/list/" + \
    #     str(uid) + "_" + str(slice_by) + "_" + \
    #     str(page_count) + "_" + str(is_basic)
    # redis_result = redis_instance.getRedisValueByKey(redis_key)
    # if redis_result != None:
    #     print("cached channel/list")
    #     return response.make_response("System", redis_result, 200)

    priority_list = priority.get_channel_prioritys_by_user(uid)
    channelList = []
    channel_count = 0
    d: telethon.tl.custom.dialog.Dialog
    async for d in user.iter_dialogs():
        channel_pri = -1
        # if d.is_group:
        #     print(d.entity)
        #     print(d.dialog)
        #     user_list = await user.get_participants(d.entity)
        #     for u in user_list:
        #         user_profile = await user.download_profile_photo(u, file=bytes)
        #         if user_profile != None:
        #             tmp_image = Image.open(io.BytesIO(user_profile))
        #             tmp_image.show()
        #             # tmp_image.thumbnail([64, 64], Image.ANTIALIAS)
        #             buf = io.BytesIO(user_profile)
        #             # tmp_image.save(buf, format="png")
        #             byte_thumb = buf.getvalue()
        #             b64 = base64.b64encode(byte_thumb)
        #             b64 = b64.decode()
        #             # print(b64)
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

        channel_dto = DTOs.ChannelDTO(
            d.entity.id, d.name, channel_pri, b64, d.unread_count)
        channelList.append(channel_dto.__dict__)
        # print(f"channel id: {channel_dto.id}, channel name: {channel_dto.name}")
        # channelData = await user.get_entity(d.entity.id)
        # print(d)
        channel_count += 1

    if page_count != -1:
        channelList = channelList[page_count *
                                  slice_by: (page_count + 1) * slice_by]

    # if is_basic == False:
    #     redis_instance.setRedisKeyAndValue(redis_key, channelList)

    return response.make_response("System", channelList, 200)


"""
job:    get other users' photo
route:  GET "/channel/photo/<uid>"
input:  user_list: list of user id split by ','
output: list of participant: { id: user id, b64: base 64 photo }
note:   use to get photo in group channel
"""


@blueprint.get("/channel/photo/<uid>")
@jwt_required
async def photo_list(uid):
    user_jwt = get_jwt_claims()
    if int(uid) != int(user_jwt["uid"]):
        return response.make_response("System", "Unauthorized", 401)

    client: TelegramClient = await utils.find_user(utils.client_list, int(uid))
    if client == None:
        return response.make_response("System", "user not found / not login", 404)

    user_list = request.args.get("user_list")
    if user_list == None:
        return response.make_response("System", "lack of user list", 400)

    redis_key = "/channel/photo/" + str(uid) + "_" + str(user_list)
    redis_result = redis_instance.getRedisValueByKey(redis_key)
    if redis_result != None:
        print("cached channel/photo")
        return response.make_response("System", redis_result, 200)

    user_list = user_list.split(",")

    participants = []
    for u in user_list:
        user_entity = None
        try:
            user_entity = await client.get_entity(int(u))
        except:
            return response.make_response("System", "user in user list not found", 404)

        participant = DTOs.userPhotoDTO(u, "")
        user_profile = await client.download_profile_photo(user_entity, file=bytes)
        if user_profile != None:
            tmp_image = Image.open(io.BytesIO(user_profile))
            # tmp_image.thumbnail([64, 64], Image.ANTIALIAS)
            buf = io.BytesIO(user_profile)
            # tmp_image.save(buf, format="png")
            byte_thumb = buf.getvalue()
            b64 = base64.b64encode(byte_thumb)
            b64 = b64.decode()
            participant.b64 = b64
            # print(b64)
        participants.append(participant.__dict__)

    redis_instance.setRedisKeyAndValue(redis_key, participants)

    return response.make_response("System", participants, 200)
