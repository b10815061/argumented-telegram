from route.channel import blueprint as channel_blueprint
from route.message import blueprint as message_blueprint
from route.setting import blueprint as setting_blueprint
from route.conn import blueprint as conn_blueprint
from route.base import blueprint as base_blueprint
from route.priority import blueprint as priority_blueprint
from route.important_msg import blueprint as important_msg_blueprint
from quart_cors import cors
from quart import Quart
from quart_jwt_extended import JWTManager
import os
import socketio
import uvicorn
import route.util as utils
import sys
from dotenv import load_dotenv
import response
import logging
import redis_instance

load_dotenv()  # take environment variables from .env.


if os.getenv("FROM") is None:
    sys.exit("FATAL : local enviroment variable FROM not set.")
host = "0.0.0.0" if os.getenv("FROM") == "DOCKER" else "127.0.0.1"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

app = Quart(__name__)

# Setup the Quart-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "tuna-birdy-UN"
jwt = JWTManager(app)

# it's used to get custom user claim for jwt auth
# jwt include: uid = user id, phone = user phone
@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return {"uid": identity["uid"], "phone": identity["phone"]}

# set up cors rules
app = cors(app_or_blueprint=app,
           allow_headers=["content-type"],
           allow_methods=["GET", "POST", "DELETE"],
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
    if (err_msg["className"] == "NotFound"):
        return response.make_response("System", err_msg, 404)
    return response.make_response("System", err_msg, 500)


sio_app = socketio.ASGIApp(utils.sio, app, socketio_path="socket.io")

utils.init()

if __name__ == "__main__":
    # uvicorn.run(sio_app, port=5000, host=host,
    #             ssl_certfile="server.crt", ssl_keyfile="server.key")
    uvicorn.run(sio_app, port=5000, host=host)
