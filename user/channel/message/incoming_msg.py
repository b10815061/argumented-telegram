from sqlite3 import Timestamp
from urllib import response
import telethon
from . import util as message_utils
from telethon.sync import events
# from quart import websocket
import route.util as utils
import route.DTOs as DTOs
import logging


def listen_on(sid, client_list, me):
    """ hook on incoming messages,
    return -> (json) : 
    [tag: tag to be parsed, 
    channel : the channel received the message, 
    from : the sender fullname/channel title, 
    data : message context, 
    messageID : the messageID, 
    timestamp : the message timestamp]
    """
    @client_list[me.id].on(events.NewMessage())
    async def onMessage(event):

        logging.info(f"{event.message.id} for {me.id}")
        channel: telethon.Channel = await event.get_chat()
        sender_id, sender = await message_utils.get_sender(event.message, client_list[me.id], channel)
        if (sender_id is None):
            sender_id = channel.id
        timestamp = event.message.date
        tag, context = await message_utils.context_handler(me.id, client_list[me.id], event.message)
        message_id = event.message.id
        # obj = {
        #     "tag": tag,
        #     "channel_id": channel.id,
        #     "sender_id": sender_id,
        #     "sender_name": sender,
        #     "content": context,
        #     "message_id": message_id,
        #     "timestamp": str(timestamp)
        # }
        obj = DTOs.MessageDTO(sender_id=sender_id, sender_name=sender, channel_id=channel.id,
                              message_id=message_id, content=context, timestamp=str(timestamp), tag=tag)
        await utils.sio.emit("message", obj.__dict__, sid)
