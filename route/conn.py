from quart import Blueprint, request  # , websocket
# from quart_cors import route_cors
from telethon.sync import TelegramClient
from user.channel.message import incoming_msg
from quart_jwt_extended import jwt_optional, get_jwt_claims, create_access_token, jwt_required
import response
import route.util as utils
import telethon
import os
import logging
import datetime
blueprint = Blueprint("connection", __name__)

# jwt logic: need to login first = jwt_require & check, don't need to login = nothing, loginning = jwt_optional


@blueprint.route("/disconnect")
@jwt_required
async def disconnect():
    """
    remove the connection of python - telegram.
    params(json) : [userid : the telegram userID]
    returns -> 200 : success / TODO : 404
    """
    try:
        userID: str = (request.args.get("user_id"))

        user_jwt = get_jwt_claims()
        if int(userID) != int(user_jwt["uid"]):
            return response.make_response("System", "Unauthorized", 401)

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
@jwt_optional
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

        # verify jwt phone with input phone to authorize correct user
        # need to add "Bearer " before the token in input
        user_jwt = get_jwt_claims()
        jwt_phone = ""

        if user_jwt:
            jwt_phone = user_jwt["phone"]

        client = TelegramClient(phone, utils.api_id, utils.api_hash)
        await client.connect()
        if jwt_phone == phone and await utils.has_session(client, phone):
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
            await client.send_code_request(phone)
            # This line should be added as client can only provide unique phone number
            utils.client_list[phone] = client
            return response.make_response("System", "please enter the code received in your telegram app", 200)
    except Exception as e:
        os.remove(f"{phone}.session")
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

    expires = datetime.timedelta(days=30)
    # need to add "Bearer " before the token
    access_token = create_access_token(
        identity={"uid": me.id, "phone": phone}, expires_delta=expires)

    res = {}
    res["id"] = me.id
    res["username"] = me.username
    res["access_hash"] = me.access_hash
    res["first_name"] = me.first_name
    res["last_name"] = me.last_name
    res["phone"] = me.phone
    res["profile_pic"] = profile_pic_data
    res["access_token"] = "Bearer " + access_token

    # Change from Phone to User ID
    utils.client_list[me.id] = utils.client_list[phone]
    del utils.client_list[phone]

    return response.make_response("System", res, 200)


# Check authorized yet or not
@blueprint.post('/checkConnection')
@jwt_required
async def checkConnection():
    try:
        data = await request.get_json()
        uid = data["uid"]
        user_jwt = get_jwt_claims()
        if int(uid) != int(user_jwt["uid"]):
            return response.make_response("System", "Unauthorized", 401)

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

    logging.info(f" ==== {userid} profile_sent ====")

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

    # user_jwt = get_jwt_claims()
    # if int(uid) != int(user_jwt["uid"]):
    #     return response.make_response("System", "Unauthorized", 401)

    try:
        await utils.client_list[uid].log_out()
    except:
        return response.make_response("System", "Logout failed", 400)

    return response.make_response("System", "Logout Success", 200)
