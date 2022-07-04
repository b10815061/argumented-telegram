import telethon
from . import util
from telethon.sync import events


def listen_on(client_list, me):  # hook on incoming messages
    @client_list[me.id].on(events.NewMessage())
    async def onMessage(event):
        channel: telethon.Channel = await event.get_chat()
        sender: str = util.get_sender(event, channel)
        time_stamp = event.message.data
