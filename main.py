from asyncio import events
from tkinter import N
from quart import Quart, render_template, request, websocket
from telethon.sync import TelegramClient
from typing import Any
from user.channel.message import incoming_msg
import os
import asyncio
import response
import telethon
import socketio
import uvicorn

import route.util as utils
from route.base import blueprint as base_blueprint
from route.conn import blueprint as conn_blueprint
from route.setting import blueprint as setting_blueprint
from route.send import blueprint as send_blueprint
# from func_test.blue import blueprint as testing_blueprint

utils.init()

app = Quart(__name__)

# api_id = 12655046
# api_hash = 'd84ab8008abfb3ec244630d2a6778fc6'
# client_list = dict()

app.register_blueprint(base_blueprint)
app.register_blueprint(conn_blueprint)
app.register_blueprint(send_blueprint)
app.register_blueprint(setting_blueprint)
# app.register_blueprint(testing_blueprint)

sio_app = socketio.ASGIApp(utils.sio, app)

# # determine the given phone is valid and return True if client login successfully
# async def login(client, phone) -> bool:
#     if not await client.is_user_authorized():
#         try:
#             await client.send_code_request(phone)
#             context = "please enter the code received in your telegram app"
#             await websocket.send(response.make_response("system", context))
#             code = await websocket.receive()
#             await client.sign_in(phone, code)
#             return True
#         except Exception as e:
#             print(e)
#             return False
#     else:
#         return True


# async def make_folder(client_id) -> str:
#     path = f'./user/{client_id}'
#     if not os.path.exists(path):
#         os.makedirs(path)
#         return ""
#     else:
#         return response.make_response("system", "Error making folder", 500)


# async def find_user(client_list, userID) -> telethon.client:
#     if userID in client_list:
#         return client_list[userID]
#     else:
#         return NULL


# @app.route("/disconnect")
# async def disconnect():
#     userID = request.args.get("user_id")
#     user = await find_user(client_list, userID)
#     if user != NULL:
#         await user.disconnect()
#         return response.make_response("system", "log out successfully")
#     else:
#         return response.make_response("system", "user not found")


# @app.websocket("/conn")
# async def conn():  # listen on incoming connection
#     while True:
#         phone = await websocket.receive()
#         client = TelegramClient(phone, api_id, api_hash)
#         await client.connect()
#         if await login(client, phone):
#             user = await client.get_me()
#             client_list[user.id] = client  # append into client list

#             await websocket.send(response.make_response("system", f"Login as {user.id}"))
#             # create folder for further usage
#             res = await make_folder(user.id)
#             if res != "":
#                 await websocket.send(res)

#             # load profile & unread message

#             # listen on message
#             incoming_msg.listen_on(client_list, user)

#             await client.run_until_disconnected()

#         else:
#             await websocket.send(response.make_response("system", f"login aborted"))


if __name__ == "__main__":
    #asyncio.run(app.run_task())
    # asyncio.run(sio_app)
    uvicorn.run(sio_app, port=5000)
