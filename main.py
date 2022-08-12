from quart import Quart
import socketio
import uvicorn

import route.util as utils

utils.init()

from route.base import blueprint as base_blueprint
from route.conn import blueprint as conn_blueprint
from route.setting import blueprint as setting_blueprint
from route.message import blueprint as message_blueprint
from route.channel import blueprint as channel_blueprint

app = Quart(__name__)

app.register_blueprint(base_blueprint)
app.register_blueprint(conn_blueprint)
app.register_blueprint(message_blueprint)
app.register_blueprint(setting_blueprint)
app.register_blueprint(channel_blueprint)


@utils.sio.event
def connect(sid, environ):
    print("connect ", sid)

@utils.sio.event
async def chat_message(sid, data):
    print("message ", data)

@utils.sio.event
def disconnect(sid):
    print('disconnect ', sid)


sio_app = socketio.ASGIApp(utils.sio, app, socketio_path="socket.io")

if __name__ == "__main__":
    uvicorn.run(sio_app, port=5000)
