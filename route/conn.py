from quart import Blueprint, request  # , websocket
# from quart_cors import route_cors
from telethon.sync import TelegramClient
from user.channel.message import incoming_msg
import response
import route.util as utils
import telethon
import os
import logging
blueprint = Blueprint("connection", __name__)


@blueprint.route("/disconnect")
async def disconnect():
    """
    remove the connection of python - telegram.
    params(json) : [userid : the telegram userID]
    returns -> 200 : success / TODO : 404
    """
    try:
        userID: str = (request.args.get("user_id"))
        user = await utils.find_user(utils.client_list, userID)
        if user != None:
            utils.remove_from_list(utils.client_list, userID)
            # res = await utils.delete_folder(userID)
            # if res != "":
            #     return response.make_response("System", res, 200)
            await user.disconnect()
            logging.info(f"{userID} disconnected")
            return response.make_response("System", "log out successfully", 200)
        else:
            return response.make_response("System", "user not found", 404)
    except Exception as e:
        logging.error(e)
        return response.make_response("System", e, 500)


@blueprint.post("/login")
async def login() -> str:  # return userID to frontend
    """
    establish connection
    params(json) : [phone : user's phone to login telegram service]
    """
    try:
        data = await request.get_json()
        phone = data["phone"]

        try:
            os.remove(f"{phone}.session-jounral")
            logging.info('removed sessiong-jounral')
        except:
            pass

        client = TelegramClient(phone, utils.api_id, utils.api_hash)
        await client.connect()
        if await utils.has_session(client, phone):
            me = await client.get_me()
            profile_pic_data = await utils.get_profile_pic(client, me.id)

            res = {}
            res["id"] = me.id
            res["username"] = me.username
            res["access_hash"] = me.access_hash
            res["first_name"] = me.first_name
            res["last_name"] = me.last_name
            res["phone"] = me.phone
            res["profile_pic"] = profile_pic_data
            # json_data = json.dumps(res, ensure_ascii=False)

            # Change from Phone to User ID
            utils.client_list[me.id] = client

            return response.make_response("System", res, 202)
        else:
            # This line should be added as client can only provide unique phone number
            utils.client_list[phone] = client
            return response.make_response("System", "please enter the code received in your telegram app", 200)
    except Exception as e:
        logging.error(e)
        return response.make_response("System", e, 500)


@blueprint.post("/verify")
async def verify():
    """
    verify the user phone
    params(json) : [phone : user's phone to login telegram service,
    code : the code sent to the user's phone via 777000 channel]
    """
    data = await request.get_json()
    phone = data["phone"]
    code = data["code"]

    try:
        await utils.client_list[phone].sign_in(phone, code)
    except:
        return response.make_response("System", "Invalid code", 401)
    me = await utils.client_list[phone].get_me()
    profile_pic_data = await utils.get_profile_pic(utils.client_list[phone], me.id)

    res = {}
    res["id"] = me.id
    res["username"] = me.username
    res["access_hash"] = me.access_hash
    res["first_name"] = me.first_name
    res["last_name"] = me.last_name
    res["phone"] = me.phone
    res["profile_pic"] = profile_pic_data
    # json_data = json.dumps(res, ensure_ascii=False)

    # Change from Phone to User ID
    utils.client_list[me.id] = utils.client_list[phone]
    del utils.client_list[phone]

    return response.make_response("System", res, 200)


# Check authorized yet or not
@blueprint.post('/checkConnection')
async def checkConnection():
    try:
        data = await request.get_json()
        uid = data["uid"]
        client = await utils.find_user(utils.client_list, uid)

        if client != None:
            me = await client.get_me()
            profile_pic_data = await utils.get_profile_pic(client, me.id)
        else:
            return response.make_response("System", "Unauthorized", 401)

        if (me != None):
            res = {}
            res["id"] = me.id
            res["username"] = me.username
            res["access_hash"] = me.access_hash
            res["first_name"] = me.first_name
            res["last_name"] = me.last_name
            res["phone"] = me.phone
            res["profile_pic"] = profile_pic_data
            # json_data = json.dumps(result, ensure_ascii=False)
            return response.make_response("System", res, 200)
        else:
            return response.make_response("System", "Unauthorized", 401)
    except Exception as e:
        logging.error(e)
        return response.make_response("System", e, 500)


@utils.sio.event
async def conn(sid, userid):
    """
    persist the user connection and send webhook messages received by telegram
    """

    client = await utils.find_user(utils.client_list, userid)
    if client == None:
        await utils.sio.emit('conn', "uesr not found", room=sid)
        return
    user: telethon.client_describe_obj = await client.get_me()
    logging.info(f"{userid} persisting")
    # res = await utils.make_folder(user.id)
    # if res != "":
    #     await utils.sio.emit('conn', res, room=sid)

    utils.client_list[user.id] = client
    # BUG: reset client_list data after login

    dialogs: list[telethon.Dialog] = await client.get_dialogs()

    # listen on message
    incoming_msg.listen_on(sid, utils.client_list, user)

    # send profile and unread count
    await utils.send_profile(sid, dialogs, client, user.id)

    logging.info(" ==== {usedid} profile_sent ====")

# TODO: delete it or add real functions


@utils.sio.event
async def disconnect(sid):
    # print(sid, "disconnected")
    pass


# Logout
@blueprint.post('/logout')
async def logout():
    data = await request.get_json()
    uid = data["uid"]

    try:
        await utils.client_list[uid].log_out()
    except:
        return response.make_response("System", "Logout failed", 400)

    return response.make_response("System", "Logout Success", 200)
