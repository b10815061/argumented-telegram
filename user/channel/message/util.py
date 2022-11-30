import base64
import os
import telethon
import time
from typing import Any, Tuple
import json
import gzip
import logging


async def get_sender(msg_instance, user, channel_instance):
    # get the sender of the msg
    try:
        # !!! messages in Chat (2 frineds channel) has no from_id attribute
        if (msg_instance.from_id != None):
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
                if (sender_instance.deleted):
                    sender = "Deleted account"
                else:
                    logging.error("=== UNHANDLED SENDER ===")
                    logging.error(sender_instance)
        except:
            sender = sender_instance.title
    except Exception as e:
        logging.error(e)
        logging.error(channel_instance)
        logging.error(msg_instance)
        return "ERROR"
    return user_id, sender


async def get_sticker_code(Stickerpath: str) -> str:  # !!!!too slow
    data = gzip.decompress(Stickerpath)
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
            stickerPath = await client.download_media(message, file=bytes)
            context = await get_sticker_code(stickerPath)
            dic = json.loads(context)
            context = json.dumps(dic)
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
