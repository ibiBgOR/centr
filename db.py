from flask_sqlalchemy import SQLAlchemy
from main import db

class DBFeedItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text)
    type = db.Column(db.String(20))
    source = db.Column(db.String(20))
    time = db.Column(db.DateTime)

    __table_args__ = (
        db.UniqueConstraint('content', 'source', name='uk_content_source'),
    )

    def __init__(self, content, type, source, time):
        self.content = content
        self.type = type
        self.source = source
        self.time = time

    def __repr__(self):
        return 'DBFeedItem ID: ' + str(self.id)

class DBLogItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    msg = db.Column(db.Text)
    time = db.Column(db.DateTime)
    level = db.Column(db.String(5))
    trace = db.Column(db.Text)

    def __init__(self, msg, time, level, trace):
        self.msg = msg
        self.time = time
        self.level = level
        self.trace = trace

    def __repr__(self):
        return 'DBLogItem ID: ' + str(self.id) + ' Message: ' + str(self.msg)

class DBConnection:
    def __init__(self, dbpath):
        pass

    def create_tables(self):
        pass

    def insert_element(self):
        pass
