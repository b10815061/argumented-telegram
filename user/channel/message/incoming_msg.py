from sqlite3 import Timestamp
from urllib import response
import telethon
from . import util
from telethon.sync import events
from quart import websocket


def listen_on(client_list, me):  # hook on incoming messages
    @client_list[me.id].on(events.NewMessage())
    async def onMessage(event):
        channel: telethon.Channel = await event.get_chat()
        sender: str = await util.get_sender(event, channel)
        time_stamp = event.message.date
        tag, context = await util.context_handler(me.id, client_list[me.id], event.message)
        obj = {
            "tag": tag,
            "channel": channel.id,
            "from": sender,
            "data": context,
            "time_stamp": str(time_stamp)
        }
        obj = str(obj)
        obj = obj.replace("\\\'", "\'")
        obj = obj.replace(", '", ', "').replace("',", '",')
        obj = obj.replace(": '", ': "').replace("':", '":')
        obj = obj.replace("{'", '{"').replace("'}", '"}')
        obj = obj.replace("\\\\", "\\")
        print(obj)
        await websocket.send(obj)
