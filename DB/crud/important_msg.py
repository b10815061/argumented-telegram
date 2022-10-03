from sqlalchemy.orm import Session
from DB.config import engine
from DB.model import channel_important_msg

# in priority, we mainly use CREATE and GET, since we auto-detect if it's CREATE or UPDATE

# user_id = Column(String)
# channel_id = Column(String)
# important_msg_id = Column(String)


# CREATE


def create_channel_important_msg(client_id: str, channel_id: str, important_msg_id: str) -> channel_important_msg:
    with Session(engine) as session:
        message = channel_important_msg(user_id=str(
            client_id), important_msg_id=str(important_msg_id), channel_id=str(channel_id))
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

# GET


def get_channel_important_msg(client_id: str, channel_id: str, important_msg_id: str) -> channel_important_msg:
    # find if it exists
    with Session(engine) as session:
        message_list = session.query(channel_important_msg) \
            .filter(channel_important_msg.user_id == str(client_id)) \
            .filter(channel_important_msg.channel_id == str(channel_id)) \
            .filter(channel_important_msg.important_msg_id == str(important_msg_id)) \
            .first()
        return message_list

# this gets all important msgs in a channel of a user
def get_channel_important_msgs(client_id: str, channel_id: str) -> list[channel_important_msg]:
    # find if it exists
    with Session(engine) as session:
        message_list = session.query(channel_important_msg) \
            .filter(channel_important_msg.user_id == str(client_id)) \
            .filter(channel_important_msg.channel_id == str(channel_id)) \
            .order_by(channel_important_msg.important_msg_id.asc()) \
            .all()
        return message_list


def get_channel_important_msgs_by_user(client_id: str) -> list[channel_important_msg]:
    # find if it exists
    with Session(engine) as session:
        message_list = session.query(channel_important_msg) \
            .filter(channel_important_msg.user_id == str(client_id)) \
            .order_by(channel_important_msg.channel_id.asc()) \
            .all()
        return message_list

# NO UPDATE


# DELETE


def delete_channel_important_msg(client_id: str, channel_id: str, important_msg_id: str) -> bool:
    if (get_channel_important_msg(client_id, channel_id, important_msg_id) == None):
        return False
    with Session(engine) as session:
        important_msg = session.query(channel_important_msg) \
            .filter(channel_important_msg.user_id == str(client_id)) \
            .filter(channel_important_msg.channel_id == str(channel_id)) \
            .filter(channel_important_msg.important_msg_id == str(important_msg_id)) \
            .delete()
        session.commit()
    return True