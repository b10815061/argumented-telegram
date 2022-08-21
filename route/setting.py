import re
from quart import Blueprint, Request, ResponseReturnValue, request
from telethon import TelegramClient
from telethon.tl.functions.account import GetGlobalPrivacySettingsRequest, SetPrivacyRequest, GetPrivacyRequest, UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.types import InputPrivacyKeyStatusTimestamp, InputPrivacyKeyChatInvite, InputPrivacyKeyPhoneCall, InputPrivacyKeyPhoneP2P, InputPrivacyKeyForwards, InputPrivacyKeyProfilePhoto, InputPrivacyKeyPhoneNumber, InputPrivacyKeyAddedByPhone, InputPrivacyValueDisallowAll, InputPrivacyValueAllowAll
import route.util as utils
import telethon

blueprint = Blueprint("setting", __name__)

# for privacy setting type, check the link below:
# https://github.com/LonamiWebs/Telethon/wiki/Privacy-settings
typeList = [InputPrivacyKeyStatusTimestamp(), InputPrivacyKeyChatInvite(), InputPrivacyKeyPhoneCall(), InputPrivacyKeyPhoneP2P(), InputPrivacyKeyForwards(), InputPrivacyKeyProfilePhoto(), InputPrivacyKeyPhoneNumber(), InputPrivacyKeyAddedByPhone()]

"""
job:    update privacy setting
route:  POST "/setting/privacy/<id>"
input:  type: privacy type index, value: setting index(0: disallow all, 1: allow all) (json)
output: stringify setting situation, 200
"""
@blueprint.post("/setting/privacy/<id>")
async def setPrivacy(id):
    data = await request.get_json()
    ruleList = [InputPrivacyValueDisallowAll(), InputPrivacyValueAllowAll()]

    if not("type" in data) or int(data["type"]) >= len(typeList) or int(data["type"]) < 0:
        return "type not found", 404
    if not("value" in data) or int(data["value"]) >= len(ruleList) or int(data["value"]) < 0:
        return "rule not found", 404

    values = [ruleList[int(data["value"])]]
    user = utils.find_user(utils.client_list, int(id))
    if user == None:
        return "user not found / not login", 404
    await user(SetPrivacyRequest(typeList[int(data["type"])], values))
    return "OK", 200

"""
job:    get privacy setting
route:  GET "/setting/privacy/<id>"
input:  type: privacy type index(params)
output: stringify setting situation, 200
"""
@blueprint.get("/setting/privacy/<id>")
async def index(id) -> ResponseReturnValue:
    print(utils.client_list)
    print(id)
    user = utils.find_user(utils.client_list, int(id))

    if user == None:
        return "user not found / not login", 404
    typeChose = request.args.get("type")
    if typeChose == None or int(typeChose) >= len(typeList) or int(typeChose) < 0:
        return "type not found", 404

    result = await user(GetPrivacyRequest(typeList[int(typeChose)]))
    return result.stringify(), 200

"""
job:    update profile
route:  POST "/setting/profile/<id>"
input:  about: about text, first_name: first name text, last_name: last name text (json) (optional)
output: OK, 200
"""
@blueprint.post("/setting/profile/<id>")
async def updateProfile(id):
    data = await request.get_json()
    user: TelegramClient = utils.find_user(utils.client_list, int(id))
    if user == None:
        return "user not found / not login", 404
    if "about" in data:
        await user(UpdateProfileRequest(about=data["about"]))
    if "first_name" in data:
        await user(UpdateProfileRequest(first_name=data["first_name"]))
    if "last_name" in data:
        await user(UpdateProfileRequest(last_name=data["last_name"]))
    return "OK", 200

"""
job:    update user name
route:  POST "/setting/username/<id>"
input:  name: new username(json)
output: OK, 200
"""
@blueprint.post("/setting/username/<id>")
async def updateUsername(id):
    data = await request.get_json()
    user: TelegramClient = utils.find_user(utils.client_list, int(id))
    if user == None:
        return "user not found / not login", 404
    if not("name" in data):
        return "no new name", 404
    await user(UpdateUsernameRequest(data["name"]))
    return "OK", 200