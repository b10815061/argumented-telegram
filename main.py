from quart import Quart
import socketio
import uvicorn

import route.util as utils
from route.base import blueprint as base_blueprint
from route.conn import blueprint as conn_blueprint
from route.setting import blueprint as setting_blueprint
from route.send import blueprint as send_blueprint

utils.init()

app = Quart(__name__)

app.register_blueprint(base_blueprint)
app.register_blueprint(conn_blueprint)
app.register_blueprint(send_blueprint)
app.register_blueprint(setting_blueprint)

sio_app = socketio.ASGIApp(utils.sio, app)

if __name__ == "__main__":
    uvicorn.run(sio_app, port=5000)
