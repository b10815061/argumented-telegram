from route.channel import blueprint as channel_blueprint
from route.message import blueprint as message_blueprint
from route.setting import blueprint as setting_blueprint
from route.conn import blueprint as conn_blueprint
from route.base import blueprint as base_blueprint
from route.priority import blueprint as priority_blueprint
from route.important_msg import blueprint as important_msg_blueprint
from quart_cors import cors
from quart import Quart
import os
import socketio
import uvicorn
import route.util as utils
from dotenv import load_dotenv
import response

load_dotenv()  # take environment variables from .env.


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
app.register_blueprint(priority_blueprint)
app.register_blueprint(important_msg_blueprint)


@app.errorhandler(Exception)
def internelServerErrorHandler(e: Exception):
    err_msg = {
        "className": e.__class__.__name__,
        "message": e.__str__()
    }
    return response.make_response("System", err_msg, 500)


sio_app = socketio.ASGIApp(utils.sio, app, socketio_path="socket.io")

if __name__ == "__main__":
    utils.init()
    uvicorn.run(sio_app, port=5000, host="127.0.0.1")
