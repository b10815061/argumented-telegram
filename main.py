from quart import Quart
import socketio
import uvicorn

import route.util as utils
from route.base import blueprint as base_blueprint
from route.conn import blueprint as conn_blueprint
from route.setting import blueprint as setting_blueprint
from route.message import blueprint as message_blueprint
from route.channel import blueprint as channel_blueprint

utils.init()

app = Quart(__name__)

app.register_blueprint(base_blueprint)
app.register_blueprint(conn_blueprint)
app.register_blueprint(message_blueprint)
app.register_blueprint(setting_blueprint)
app.register_blueprint(channel_blueprint)


sio_app = socketio.ASGIApp(utils.sio, app)


@utils.sio.on("test")
def test():
    print("test")


if __name__ == "__main__":
    uvicorn.run(sio_app, port=5000)
