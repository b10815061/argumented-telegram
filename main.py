from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import route.util as utils
import uvicorn
import socketio
import os
from quart import Quart
from quart_cors import cors
from route.base import blueprint as base_blueprint
from route.conn import blueprint as conn_blueprint
from route.setting import blueprint as setting_blueprint
from route.message import blueprint as message_blueprint
from route.channel import blueprint as channel_blueprint


app = Quart(__name__)
app = cors(app_or_blueprint=app,
           allow_headers=["content-type"],
           allow_methods=["GET", "POST"],
           allow_origin=[os.getenv("FRONTEND_SITE")])

app.register_blueprint(base_blueprint)
app.register_blueprint(conn_blueprint)
app.register_blueprint(message_blueprint)
app.register_blueprint(setting_blueprint)
app.register_blueprint(channel_blueprint)


sio_app = socketio.ASGIApp(utils.sio, app, socketio_path="socket.io")

if __name__ == "__main__":
    uvicorn.run(sio_app, port=5000)
