import base64
from PIL import Image
from quart import websocket
import response
import os
import shutil
import telethon
import socketio


api_id = 12655046
api_hash = 'd84ab8008abfb3ec244630d2a6778fc6'
client_list = dict()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')


# determine the given phone is valid and return True if client login successfully
async def has_session(client, phone) -> bool:
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone)
            return False
        except Exception as e:
            print(e)
            return False
    else:
        return True


async def make_folder(client_id) -> str:  # create user private folder
    path = f'./user/userid{client_id}'
    if not os.path.exists(path):
        os.makedirs(path)
        return ""
    else:
        return response.make_response("system", "Error making folder", 500)


async def delete_folder(client_id) -> str:  # delete user private folder
    path = f"./user/userid{client_id}"
    if not os.path.exists(path):
        return response.make_response("system", "Error deleting folder", 500)
    else:
        shutil.rmtree(path, ignore_errors=True)
        return ""


async def get_profile_pic(client, client_id) -> str:

    # if the user has no photo, it will return None
    path = await client.download_profile_photo('me', os.path.join(os.getcwd(), f"user/userid{client_id}"))
    try:
        with open(path, 'rb') as file:
            raw_data = file.read()
            data = base64.b64encode(raw_data).decode()
        os.remove(path)
        return data
    except:
        return ""


# find the telethon Client instance
def find_user(client_list, userID) -> telethon.client:
    userID = int(userID)
    if userID in client_list:
        return client_list[userID]
    else:
        return None


def add_to_list(client_list, user_id, user):
    client_list[int(user_id)] = user


def remove_from_list(client_list, user_id):
    del client_list[int(user_id)]

# iterate through client's dialog and send unread message count back


async def send_unread_count(dialogs):
    x = []
    for d in dialogs:
        if(type(d.message.peer_id) == telethon.tl.types.PeerChannel):
            x.append([d.unread_count, d.message.peer_id.channel_id])
        elif(type(d.message.peer_id) == telethon.tl.types.PeerChat):
            x.append([d.unread_count, d.message.peer_id.chat_id])
        else:
            x.append([d.unread_count, d.message.peer_id.user_id])

    for e in x:
        unread = {
            "tag": "initial",
            "channel": e[1],
            "count": e[0]
        }
        # unread = str(unread).replace("\'", "\"")

        global sio
        await sio.emit('initial', unread)  # websocket.send(unread)


# iterate through dialog and send profile one by one
async def send_profile(dialogs, client, client_id):
    size = 64, 64
    for d in dialogs:
        if type(d.message.peer_id) == telethon.tl.types.PeerChannel:
            ID = d.message.peer_id.channel_id
        elif(type(d.message.peer_id) == telethon.tl.types.PeerChat):
            ID = d.message.peer_id.chat_id
        else:
            ID = d.message.peer_id.user_id
        path = f"./user/userid{client_id}/{ID}.png"
        # this might not download successfully if user has no profile
        await client.download_profile_photo(d, file=path, download_big=False)
        try:
            # make thumbnail
            image = Image.open(path)
            image.thumbnail(size, Image.ANTIALIAS)
            thumbpath = f"./user/userid{client_id}/{ID}_thumb.png"
            image.save(thumbpath, "PNG")

            with open(thumbpath, "rb") as file:
                raw_data = file.read()
                b64 = base64.b64encode(raw_data).decode()
            os.remove(path)
            os.remove(thumbpath)
        except:
            b64 = "no profile"
        finally:
            obj = {
                "tag": "profile",
                "b64": b64,
                "id": ID,
                "name": d.name,
                "unread_count": d.unread_count
            }

            global sio
            # websocket.send(str(obj).replace("\'", "\""))
            await sio.emit('initial', obj)


async def pong():
    global sio
    await sio.emit("pong", "pong")
