from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint

from DB.config import Base


class channel_priority(Base):
    __tablename__ = "channel_priority"
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'channel_id'),
    )

    user_id = Column(String)
    channel_id = Column(String)
    priority = Column(Integer)

class channel_announce(Base):
    __tablename__ = "channel_announce"
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'channel_id'),
    )

    user_id = Column(String)
    channel_id = Column(String)
    important_msg_id = Column(String)

class setting(Base):
    __tablename__ = "setting"
    __table_args__ = (PrimaryKeyConstraint('user_id'),)

    user_id = Column(String)
    font_size = Column(Integer)
    language = Column(String)


# database spec
# channel priority				        channel announce    				        setting		
# user_id       STRING  使用者id		user_id	            STRING	使用者id		user_id     STRING	使用者id
# channel_id    STRING	頻道id          channel_id	        STRING	頻道id		    font_size   INT     字體大小
# priority	    INT 	優先度          important_msg_id	STRING	定選訊息id		language    STRING	使用語言
