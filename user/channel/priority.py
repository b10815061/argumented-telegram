from sqlalchemy.orm import Session
from DB.config import engine
from DB import model


async def insert_user_channel(client_id, input_channel, input_pri):
    # find if it exists
    with Session(engine) as session:
        star_channel = channels(user_id=str(
            client_id), priority=input_pri, channel_id=str(input_channel), message="")
        session.add(star_channel)
        session.commit()
        return


async def retrive_prior(client_id, input_channel):
    # find if it exists
    with Session(engine) as session:
        channel = session.query(channels)\
            .filter(channels.user_id == str(client_id))\
            .filter(channels.channel_id == str(input_channel))\
            .first()
        return (channel.priority if channel != None else -1)

# return 10 tuples for a given user


async def retrive_all(client_id):
    # find if it exists
    with Session(engine) as session:
        channel = session.query(channels)\
            .filter(channels.user_id == str(client_id))\
            .order_by(channels.priority.asc())\
            .all()
        return (channel)


async def set_pri(channel_id, pri):
    with Session(engine) as session:
        channel = session.query(channels)\
            .filter(channels.channel_id == str(channel_id))\
            .update({'priority': int(pri)})

        session.commit()
    return
