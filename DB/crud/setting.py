from sqlalchemy.orm import Session
from DB.config import engine
from DB.model import setting as Setting

# in setting, we mainly use CREATE and GET, since we auto-detect if it's CREATE or UPDATE

# user_id = Column(String)
# font_size = Column(Integer)
# language = Column(String)


# CREATE


def create_setting(user_id: str, font_size: int, language: str, bubble_count: int) -> Setting:
    # if exist then update
    if (get_setting(user_id) != None):
        return update_setting(user_id, font_size, language)

    if (font_size == None):
        font_size = 1
    if (language == None):
        language = "en"
    if (bubble_count == None):
        bubble_count = 10

    with Session(engine) as session:
        setting = Setting(user_id=str(
            user_id), font_size=font_size, language=str(language), bubble_count=bubble_count)
        session.add(setting)
        session.commit()
        session.refresh(setting)
        return setting

# GET


def get_setting(user_id: str) -> Setting:
    with Session(engine) as session:
        setting = session.query(Setting) \
            .filter(Setting.user_id == str(user_id)) \
            .first()
        return setting

# UPDATE


def update_setting(user_id: str, font_size: int, language: str, bubble_count: int) -> Setting:
    # if not exist then create
    original_setting = get_setting(user_id)
    if (original_setting == None):
        return create_setting(user_id, font_size, language, bubble_count)

    if (font_size == None):
        font_size = original_setting.font_size
    if (language == None):
        language = original_setting.language
    if (bubble_count == None):
        bubble_count = original_setting.bubble_count

    with Session(engine) as session:
        setting = session.query(Setting) \
            .filter(Setting.user_id == str(user_id)) \
            .update({'font_size': int(font_size), 'language': language, 'bubble_count': bubble_count})
        session.commit()
        setting = session.query(Setting) \
            .filter(Setting.user_id == str(user_id)) \
            .first()
    return setting


# NO NEED TO DELETE


# def delete_setting(user_id: str) -> bool:
#     if (get_setting(user_id) == None):
#         return False
#     with Session(engine) as session:
#         setting = session.query(Setting) \
#             .filter(Setting.user_id == str(user_id)) \
#             .delete()
#         session.commit()
#     return True
