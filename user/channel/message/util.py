import base64
import os
import telethon
import pyrlottie
import time
from typing import Any, Tuple


async def get_sender(msg_instance, user, channel_instance):
    # get the sender of the msg
    try:
        # !!! messages in Chat (2 frineds channel) has no from_id attribute
        if(msg_instance.from_id != None):
            sender_instance = await user.get_entity(msg_instance.from_id.user_id)
            user_id = msg_instance.from_id.user_id
        else:
            # which menas if the from_id is NoneType, then the channel itself is a user
            sender_instance = channel_instance
            user_id = None
        try:
            if sender_instance.username != None:
                sender = sender_instance.username
            elif sender_instance.first_name != None:
                lname = sender_instance.last_name if sender_instance.last_name != None else ""
                sender = sender_instance.first_name + lname
            else:
                print("AN ERROR MIGHT OCCUR")
                print(sender_instance, end="\n\n\n")
                sender = "Deleted account"
        except:
            sender = sender_instance.title
    except Exception as e:
        print(e)
        print(channel_instance)
        print(msg_instance)
        return "ERROR"
    return user_id, sender


async def get_sticker_code(cur: int, Stickerpath: str, client_id) -> str:  # !!!!too slow
    print("entering lock")
    path = f"./user/userid{client_id}/{cur}.gif"
    await pyrlottie.convSingleLottie(lottieFile=pyrlottie.LottieFile(Stickerpath), destFiles=[path])
    # send byte index to frontend
    with open(path, 'rb') as file:
        gif_data = file.read()
        data = base64.b64encode(gif_data).decode()
    os.remove(Stickerpath)
    os.remove(path)
    print("out of lock")
    return data


async def outline_context_handler(message) -> Tuple[str, str]:
    tag: str = ""
    context: str = ""
    if type(message.media) == telethon.tl.types.MessageMediaPhoto:
        tag = "image"
        context = "send an image"
    elif type(message.media) == telethon.tl.types.MessageMediaDocument:
        mime_type = message.media.document.mime_type
        if mime_type == "video/mp4":
            tag = "mp4"
            context = "send a video"
        elif mime_type == "application/x-tgsticker":
            tag = "gif"
            context = "send a sticker"
        elif mime_type == "audio/ogg":
            tag = "audio"
            context = "send an audio"
        elif mime_type == "application/pdf":
            tag = "pdf"
            context = "send a pdf"
    else:
        tag = "message"
        data = message.message
        try:
            context = data.replace("\\", "\\\\").replace("\"", "\\\"")
        except:
            context = data

    return tag, context


async def context_handler(client_id, client, message) -> Tuple[str, str]:
    tag: str = ""
    context: str = ""
    if type(message.media) == telethon.tl.types.MessageMediaPhoto:
        tag = "image"
        context = await get_file_code(client_id, client, message)
    elif type(message.media) == telethon.tl.types.MessageMediaDocument:
        mime_type = message.media.document.mime_type
        if mime_type == "video/mp4":
            tag = "mp4"
            context = await get_file_code(client_id, client, message)
        elif mime_type == "application/x-tgsticker":
            tag = "gif"
            stickerPath = await client.download_media(message, file=f"./user/userid{client_id}")
            context = await get_sticker_code(time.time_ns(), stickerPath, client_id)
        elif mime_type == "audio/ogg":
            tag = "audio"
            context = await get_file_code(client_id, client, message)
        elif mime_type == "application/pdf":
            tag = "pdf"
    else:
        tag = "message"
        data = message.message
        try:
            context = data.replace("\\", "\\\\").replace("\"", "\\\"")
        except:
            context = data

    return tag, context


# available for : photo, gif, audio
async def get_file_code(client_id, client, message) -> str:
    path = await client.download_media(message, file=f"./user/userid{client_id}/")
    with open(path, 'rb') as file:
        raw_data = file.read()
        data = base64.b64encode(raw_data).decode()
    os.remove(path)
    return data
