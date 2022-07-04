import telethon
from typing import Any


async def get_sender(event, channel) -> str:
    try:
        sender_instance: telethon.Peer = await event.get_sender()
        if sender_instance.username != None:
            sender = sender_instance.username
        elif sender_instance.first_name != None:
            lname = sender_instance.last_name if sender_instance.last_name != None else ""
            sender = sender_instance.first_name + lname
        else:
            sender = sender_instance.title
    except:  # for those channels containing anonymous users
        sender = channel.title
    return sender


def context_handler(message):
    if type(message.media) == telethon.ti.types.MessageMediaPhoto:
        tag = "image"
    elif type(message.media) == telethon.ti.types.MessageMediaDocument:
        mime_type = message.media.document.mime_type
        if mime_type == "video/mp4":
            tag = "mp4"
        elif mime_type == "application/x-tgsticker":
            tag = "gif"
        elif mime_type == "audio/ogg":
            tag = "audio"
        elif mime_type == "application/pdf":
            tag = "pdf"
    else:
        tag = "message"
        data = message.message
        data = data.replace("\\", "\\\\")
        data = data.replace("\"", "\\\"")
