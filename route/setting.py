import re
from quart import Blueprint, Request, ResponseReturnValue, request
from telethon import TelegramClient, types
from telethon.tl.functions.account import GetGlobalPrivacySettingsRequest, SetPrivacyRequest, GetPrivacyRequest, UpdateProfileRequest, UpdateUsernameRequest, ChangePhoneRequest, SendChangePhoneCodeRequest
from telethon.tl.types import InputPrivacyKeyStatusTimestamp, InputPrivacyKeyChatInvite, InputPrivacyKeyPhoneCall, InputPrivacyKeyPhoneP2P, InputPrivacyKeyForwards, InputPrivacyKeyProfilePhoto, InputPrivacyKeyPhoneNumber, InputPrivacyKeyAddedByPhone, InputPrivacyValueDisallowAll, InputPrivacyValueAllowAll
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.errors.rpcerrorlist import PhoneNumberOccupiedError, PhoneNumberInvalidError
import route.util as utils
import telethon
import base64
import response

blueprint = Blueprint("setting", __name__)

# for privacy setting type, check the link below:
# https://github.com/LonamiWebs/Telethon/wiki/Privacy-settings
typeList = [InputPrivacyKeyStatusTimestamp(), InputPrivacyKeyChatInvite(), InputPrivacyKeyPhoneCall(), InputPrivacyKeyPhoneP2P(), InputPrivacyKeyForwards(), InputPrivacyKeyProfilePhoto(), InputPrivacyKeyPhoneNumber(), InputPrivacyKeyAddedByPhone()]
typenameList = ["StatusTimestamp", "ChatInvite", "PhoneCall", "PhoneP2P", "Forwards", "ProfilePhoto", "PhoneNumber", "AddedByPhone"]

"""
job:    get privacy setting
route:  GET "/setting/privacy/<id>"
input:  no input
output: stringify setting situation, 200
"""
@blueprint.get("/setting/privacy/<id>")
async def index(id) -> ResponseReturnValue:
    print(utils.client_list)
    print(utils.session_list)
    print(id)
    user = await utils.find_user(utils.client_list, int(id))
    if user == None:
        return response.make_response("System", "user not found / not login", 404)
    results = []
    for requestType in typeList:
        result = await user(GetPrivacyRequest(requestType))
        results.append(result.to_dict())
    return response.make_response("System", results, 200)

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

    user = await utils.find_user(utils.client_list, int(id))
    if user == None:
        return response.make_response("System", "user not found / not login", 404)

    for idx, typeName in enumerate(typenameList):
        if (typeName in data):
            if int(data[typeName]) >= len(ruleList) or int(data[typeName]) < 0:
                return response.make_response("System", "wrong rule", 400)
            values = [ruleList[int(data[typeName])]]
            await user(SetPrivacyRequest(typeList[idx], values))

    return response.make_response("System", "OK", 200)

"""
job:    update profile
route:  POST "/setting/profile/<id>"
input:  about: about text, first_name: first name text, last_name: last name text (json) (optional)
output: OK, 200
"""
@blueprint.post("/setting/profile/<id>")
async def updateProfile(id):
    data = await request.get_json()
    user: TelegramClient = await utils.find_user(utils.client_list, int(id))
    if user == None:
        return response.make_response("System", "user not found / not login", 404)
    if "about" in data:
        await user(UpdateProfileRequest(about=data["about"]))
    if "first_name" in data:
        await user(UpdateProfileRequest(first_name=data["first_name"]))
    if "last_name" in data:
        await user(UpdateProfileRequest(last_name=data["last_name"]))
    return response.make_response("System", "OK", 200)

"""
job:    update user name
route:  POST "/setting/username/<id>"
input:  name: new username(json)
output: OK, 200
"""
@blueprint.post("/setting/username/<id>")
async def updateUsername(id):
    data = await request.get_json()
    user: TelegramClient = await utils.find_user(utils.client_list, int(id))
    if user == None:
        return response.make_response("System", "user not found / not login", 404)
    if not("name" in data):
        return response.make_response("System", "no new name", 404)
    await user(UpdateUsernameRequest(data["name"]))
    return response.make_response("System", "OK", 200)

"""
job:    update profile photo
route:  POST "/setting/photo/<id>"
input:  photo: new photo in base64 (json)
output: OK, 200
"""
@blueprint.post("/setting/photo/<id>")
async def updatePhoto(id):
    data = await request.get_json()
    user: TelegramClient = await utils.find_user(utils.client_list, int(id))
    if user == None:
        return response.make_response("System", "user not found / not login", 404)
    if not("photo" in data):
        return response.make_response("System", "no new photo", 404)
    file = base64.b64decode(s=data["photo"])
    await user(UploadProfilePhotoRequest(await user.upload_file(file)))
    return response.make_response("System", "OK", 200)

"""
job:    send update phone code request
route:  POST "/setting/phone/code/<id>"
input:  phone: new phone number (json)
output: phone_code_hash & other related result, 200
"""
# TODO: may need to save phone_code_hash
@blueprint.post("/setting/phone/code/<id>")
async def sendUpdatePhoneCodeRequest(id):
    data = await request.get_json()
    user: TelegramClient = await utils.find_user(utils.client_list, int(id))
    if not("phone" in data):
        return response.make_response("System", "no new phone", 400)
    try:
        result: types.auth.SentCode = user(SendChangePhoneCodeRequest(
            phone_number=data["phone"],
            settings=types.CodeSettings(
                allow_flashcall=True,
                current_number=True,
                allow_app_hash=True
            )
        ))
        return response.make_response("System", result.to_dict(), 200)
    except PhoneNumberOccupiedError:
        return response.make_response("System", "The phone number is already in use", 400)
    except PhoneNumberInvalidError:
        return response.make_response("System", "The phone number is invalid", 400)
    except:
        return response.make_response("System", "Internal Server Error", 500)

"""
job:    varify phone change request
route:  POST "/setting/phone/varify/<id>"
input:  phone: new phone number (json)
output: phone_code_hash & other related result, 200
"""
@blueprint.post("/setting/phone/varify/<id>")
async def varifyPhoneChnageRequest(id):
    data = await request.get_json()
    user: TelegramClient = await utils.find_user(utils.client_list, int(id))
    if not("phone" in data):
        return response.make_response("System", "no phone number", 400)
    if not("code_hash" in data):
        return response.make_response("System", "no code hash", 200)
    if not("code" in data):
        return response.make_response("System", "no phone code", 200)
    try:
        result = user(ChangePhoneRequest(
            phone_number = data["phone"],
            phone_code_hash = data["code_hash"],
            phone_code = data["code"]
        ))
        return response.make_response("System", "OK", 200)
    except PhoneNumberOccupiedError:
        return response.make_response("System", "The phone number is already in use", 400)
    except PhoneNumberInvalidError:
        return response.make_response("System", "The phone number is invalid", 400)
    except:
        return response.make_response("System", "Internal Server Error", 500)