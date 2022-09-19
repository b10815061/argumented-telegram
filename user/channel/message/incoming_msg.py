from sqlite3 import Timestamp
from urllib import response
import telethon
from . import util as message_utils
from telethon.sync import events
# from quart import websocket
import route.util as utils


def listen_on(client_list, me):
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
        print("message incoming : \n")
        print(event.message)
        channel: telethon.Channel = await event.get_chat()
        sender_id, sender = await message_utils.get_sender(event.message, client_list[me.id], channel)
        if(sender_id is None):
            sender_id = channel.id
        timestamp = event.message.date
        tag, context = await message_utils.context_handler(me.id, client_list[me.id], event.message)
        message_id = event.message.id
        obj = {
            "tag": tag,
            "channel": channel.id,
            "sender_id": sender_id,
            "from": sender,
            "data": context,
            "message_id": message_id,
            "timestamp": str(timestamp)
        }
        # obj = str(obj)
        # obj = obj.replace("\\\'", "\'")
        # obj = obj.replace(", '", ', "').replace("',", '",')
        # obj = obj.replace(": '", ': "').replace("':", '":')
        # obj = obj.replace("{'", '{"').replace("'}", '"}')
        # obj = obj.replace("\\\\", "\\")
        # print(obj)
        await utils.sio.emit("message", obj)
