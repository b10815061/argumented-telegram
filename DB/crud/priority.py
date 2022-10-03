from sqlalchemy.orm import Session
from DB.config import engine
from DB.model import channel_priority

# in priority, we mainly use CREATE and GET, since we auto-detect if it's CREATE or UPDATE

# user_id = Column(String)
# channel_id = Column(String)
# priority = Column(Integer)


# CREATE


def create_channel_priority(client_id: str, channel_id: str, priority: str) -> channel_priority:
    # if exist then update
    if (get_channel_priority(client_id, channel_id) != None):
        return update_channel_priority(client_id, channel_id, priority)

    with Session(engine) as session:
        channel = channel_priority(user_id=str(
            client_id), priority=priority, channel_id=str(channel_id))
        session.add(channel)
        session.commit()
        session.refresh(channel)
        return channel

# GET


def get_channel_priority(client_id: str, channel_id: str) -> channel_priority:
    with Session(engine) as session:
        channel = session.query(channel_priority) \
            .filter(channel_priority.user_id == str(client_id)) \
            .filter(channel_priority.channel_id == str(channel_id)) \
            .first()
        return channel


def get_channel_prioritys_by_user(client_id: str) -> list[channel_priority]:
    with Session(engine) as session:
        channel_list = session.query(channel_priority) \
            .filter(channel_priority.user_id == str(client_id)) \
            .order_by(channel_priority.priority.asc()) \
            .all()
        return channel_list

# UPDATE


def update_channel_priority(client_id: str, channel_id: str, priority: str) -> channel_priority:
    with Session(engine) as session:
        channel = session.query(channel_priority) \
            .filter(channel_priority.user_id == str(client_id)) \
            .filter(channel_priority.channel_id == str(channel_id)) \
            .update({'priority': int(priority)})
        session.commit()
        channel = session.query(channel_priority) \
            .filter(channel_priority.user_id == str(client_id)) \
            .filter(channel_priority.channel_id == str(channel_id)) \
            .first()
    return channel


# NO NEED TO DELETE


# def delete_channel_priority(client_id: str, channel_id: str) -> bool:
#     if (get_channel_priority(client_id, channel_id) == None):
#         return False
#     with Session(engine) as session:
#         channel = session.query(channel_priority) \
#             .filter(channel_priority.user_id == str(client_id)) \
#             .filter(channel_priority.channel_id == str(channel_id)) \
#             .delete()
#         session.commit()
#     return True