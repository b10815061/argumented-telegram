import re
from quart import Blueprint, Request, ResponseReturnValue, request
from telethon import TelegramClient
from telethon.tl.functions.account import GetGlobalPrivacySettingsRequest, SetPrivacyRequest, GetPrivacyRequest
from telethon.tl.types import InputPrivacyKeyStatusTimestamp, InputPrivacyValueDisallowAll, InputPrivacyKeyChatInvite, InputPrivacyKeyPhoneCall, InputPrivacyValueAllowAll
import route.util as utils
import telethon

blueprint = Blueprint("setting", __name__)

@blueprint.post("/privacyset/<userID>")
async def setPrivacy(userID):
    data = await request.get_json()
    typeList = [InputPrivacyKeyStatusTimestamp(), InputPrivacyKeyChatInvite(), InputPrivacyKeyPhoneCall()]
    ruleList = [InputPrivacyValueDisallowAll(), InputPrivacyValueAllowAll()]
    values = [ruleList[int(data["value"])]]
    user: TelegramClient = await find_user(utils.client_list, int(userID))
    await user(SetPrivacyRequest(typeList[int(data["type"])], values))
    return "200", 200

@blueprint.get("/privacyset/<userID>")
async def index(userID) -> ResponseReturnValue:
    print(utils.client_list)
    print(userID)
    user: TelegramClient = await utils.find_user(utils.client_list, int(userID))
    if user == None:
        return "user not found / not login", 404
    typeList = [InputPrivacyKeyStatusTimestamp(), InputPrivacyKeyChatInvite(), InputPrivacyKeyPhoneCall()]
    typeChose = request.args.get("type")
    result = await user(GetPrivacyRequest(typeList[int(typeChose)]))
    return result.stringify(), 200

