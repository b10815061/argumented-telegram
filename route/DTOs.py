class MessageDTO:
    def __init__(self, sender_id, sender_name, channel_id, message_id, content, timestamp, tag):
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.channel_id: int = channel_id
        self.message_id = message_id
        self.content: str = content
        self.timestamp: str = timestamp
        self.tag: str = tag


class ChannelDTO:
    def __init__(self, channel_id, channel_name, priority, b64, unread_count):
        self.id = channel_id
        self.name = channel_name
        self.priority = priority
        self.b64 = b64
        self.unread_count = unread_count


class UISettingDTO:
    def __init__(self, user_id, font_size, language):
        self.id = user_id
        self.font_size = font_size
        self.language = language
