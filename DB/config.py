from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, String

from dotenv import load_dotenv
import os

load_dotenv()


SQLALCHEMY_DATABASE_URL = "postgresql://tommy:astrongpassword@db:5432/telegram" if os.getenv(
    "FROM") == "DOCKER" else "postgresql://tommy:0000@localhost:5432/telegram"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


metadata = MetaData()
channel_priority = Table('channel_priority', metadata,
                         Column('user_id', String),
                         Column('channel_id', String),
                         Column('priority', Integer)
                         )

channel_important_msg = Table('channel_important_msg', metadata,
                              Column('user_id', String),
                              Column('channel_id', String),
                              Column('important_msg_id', String)
                              )

setting = Table('ui_setting', metadata,
                Column('user_id', String),
                Column('font_size', Integer),
                Column('language', String),
                Column('bubble_count', Integer)
                )

metadata.create_all(engine)

Base = declarative_base()  # inherit from this class to create ORM models
