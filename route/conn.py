from quart import Blueprint, request  # , websocket
from quart_cors import route_cors
from telethon.sync import TelegramClient
from user.channel.message import incoming_msg
import response
import route.util as utils
import telethon
import json

blueprint = Blueprint("connection", __name__)


@blueprint.route("/disconnect")
async def disconnect():
    """
    remove the connection of python - telegram.
    params(json) : [userid : the telegram userID]
    returns -> 200 : success / TODO : 404
    """
    userID: str = (request.args.get("user_id"))
    user = utils.find_user(utils.client_list, userID)
    if user != None:
        utils.remove_from_list(utils.client_list, userID)
        res = await utils.delete_folder(userID)
        if res != "":
            return res
        await user.disconnect()
        return response.make_response("System", "log out successfully")
    else:
        return response.make_response("System", "user not found")


# @blueprint.websocket("/a")
@utils.sio.event
async def a(phone):  # listen on incoming connection
    """
    DEPRECATED ENDPOINT, ONLY FOR TESTING
    USE /login AND /conn INSTEAD (RESTFUL FOR SIGN IN, AND SOCKET FOR PERSISTING)
    """
    client = TelegramClient(phone, utils.api_id, utils.api_hash)
    await client.connect()
    if await utils.has_session(client, phone):
        user: telethon.client_describe_obj = await client.get_me()
        # append into client list !!! todo -> might want to use token instead

        # websocket.send(response.make_response("System", f"Login as {user.id}"))
        await utils.sio.emit('a', response.make_response("System", f"Login as {user.id}"))
        # create folder for further usage
        res = await utils.make_folder(user.id)
        if res != "":
            await utils.sio.emit('a', res)  # websocket.send(res)

        utils.client_list[user.id] = client

        dialogs: list[telethon.Dialog] = await client.get_dialogs()
        # load profile
        # await utils.send_profile(dialogs, client, user.id)
        # send unread message count
        await utils.send_unread_count(dialogs)
        # listen on message
        incoming_msg.listen_on(utils.client_list, user)

        await client.run_until_disconnected()

    else:
        # websocket.send(response.make_response("System", f"login aborted"))
        await utils.sio.emit('a', response.make_response("System", f"login aborted"))


@blueprint.post("/login")
@route_cors(allow_headers=["content-type"],
            allow_methods=["POST"],
            allow_origin=["http://localhost:3000"])
async def login() -> str:  # return userID to frontend
    """
    establish connection
    params(json) : [phone : user's phone to login telegram service]
    """
    data = await request.get_json()
    phone = data["phone"]
    client = TelegramClient(phone, utils.api_id, utils.api_hash)
    await client.connect()
    if await utils.has_session(client, phone):
        me = await client.get_me()
        utils.client_list[me.id] = client
        return response.make_response("System", f"Login as {me.id}", 202)
    else:
        # This line should be added as client can only provide unique phone number
        utils.client_list[phone] = client
        return response.make_response("System", "please enter the code received in your telegram app", 200)


@blueprint.post("/verify")
@route_cors(allow_headers=["content-type"],
            allow_methods=["POST"],
            allow_origin=["http://localhost:3000"])
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
    profile_pic_data = await utils.get_profile_pic(utils.client_list[phone])

    res = {}
    res["id"] = me.id
    res["username"] = me.username
    res["access_hash"] = me.access_hash
    res["first_name"] = me.first_name
    res["last_name"] = me.last_name
    res["phone"] = me.phone
    res["profile_pic"] = profile_pic_data
    json_data = json.dumps(res, ensure_ascii=False)

    # Change from Phone to User ID
    # utils.client_list[me.id] = utils.client_list[phone]
    # del utils.client_list[phone]

    return json_data, 200

# Check authorized yet or not
@blueprint.post('/checkConnection')
@route_cors(allow_headers=["content-type"],
            allow_methods=["POST"], 
            allow_origin=["http://localhost:3000"])
async def checkConnection():
    data = await request.get_json()
    phone = data["phone"]

    if phone in utils.client_list:
        me = await utils.client_list[phone].get_me()
        profile_pic_data = await utils.get_profile_pic(utils.client_list[phone])
    else:
        return "Unauthorized_1", 400
    
    if(me != None):
        response = {}
        response["id"] = me.id
        response["username"] = me.username
        response["access_hash"] = me.access_hash
        response["first_name"] = me.first_name
        response["last_name"] = me.last_name
        response["phone"] = me.phone
        response["profile_pic"] = profile_pic_data
        json_data = json.dumps(response, ensure_ascii=False)
        return json_data, 200
    else:
        return "Unauthorized_2", 400


# @blueprint.websocket("/conn")
@utils.sio.event
async def conn(sid, userid):
    """
    persist the user connection and send webhook messages received by telegram
    """

    client = utils.find_user(utils.client_list, userid)
    user: telethon.client_describe_obj = await client.get_me()
    print(userid, "persisting")
    res = await utils.make_folder(user.id)
    if res != "":
        await utils.sio.emit('conn', res)

    utils.client_list[user.id] = client

    dialogs: list[telethon.Dialog] = await client.get_dialogs()
    # load profile
    # await utils.send_profile(dialogs, client, user.id)
    # send unread message count
    await utils.send_unread_count(dialogs)
    # listen on message
    incoming_msg.listen_on(utils.client_list, user)

# Logout
@blueprint.post('/logout')
@route_cors(allow_headers=["content-type"],
            allow_methods=["POST"],
            allow_origin=["http://localhost:3000"])
async def logout():
    data = await request.get_json()
    phone = data["phone"]
    print(phone)

    try:
        await utils.client_list[phone].log_out()
    except:
        return "Logout failed", 401

    return "Logout Success", 200


@utils.sio.event
async def test(sid):
    print("test")
    await utils.pong()
