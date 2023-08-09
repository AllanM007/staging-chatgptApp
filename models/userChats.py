from datetime import datetime
from flask import json
from sqlalchemy.ext.declarative import DeclarativeMeta
from app import db


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [
                x for x in dir(obj) if not x.startswith("_") and x != "metadata"
            ]:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(
                        data
                    )  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


class user_chats(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, nullable=False)
    userName = db.Column(db.String(200), nullable=False)
    chatPayload = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=False)
    queriesMade = db.Column(db.Integer, nullable=False)
    userDevice = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.Date, default=datetime.now)
    date = db.Column(db.DateTime, default=datetime.now)
    active = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        userId,
        userName,
        chatPayload,
        keywords,
        queriesMade,
        userDevice,
        timestamp,
        date,
        active,
    ):
        self.userId = userId
        self.userName = userName
        self.chatPayload = chatPayload
        self.keywords = keywords
        self.queriesMade = queriesMade
        self.userDevice = userDevice
        self.timestamp = timestamp
        self.date = date
        self.active = active


class user_chats_keywords(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        keyword,
        active,
    ):
        self.keyword = keyword
        self.active = active
