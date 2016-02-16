from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from main import db
from feeditem import Feeditem

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

LOG_LEVEL = [
    'INFO',
    'WARN',
    'ERROR',
    'DEBUG',
]

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
    def __init__(self):
        self.session = sessionmaker()

    def insert_element(self, element):
        s = session()

        if isinstance(element, DBLogItem) or isinstance(element, DBFeedItem):
            try:
                s.add(element)
                s.commit()
            except Exception, e:
                print str(e)
        elif isinstance(element, Feeditem):
            self.insert_element(DBFeedItem(element.content, element.type, element.source, element.time))

    def get_feeds(self, type):
        s = session()
        return s.query(DBFeedItem).filter(DBFeedItem.type == type)

    def get_logs(self, level):
        s = session()
        if level == None or level == '':
            return s.query(DBLogItem)
        elif level not in LOG_LEVEL:
            return s.query(DBLogItem).filter(DBLogItem.level == (level))
        elif level == LOG_LEVEL[0]: # INFO
            return s.query(DBLogItem).filter(DBLogItem.level == (LOG_LEVEL[0]))
        elif level == LOG_LEVEL[1]: # WARN
            return s.query(DBLogItem).filter(or_(
                DBLogItem.level == (LOG_LEVEL[0]),
                DBLogItem.level == (LOG_LEVEL[1])
            ))
        elif level == LOG_LEVEL[2]: # ERROR
            return s.query(DBLogItem).filter(or_(
                DBLogItem.level == (LOG_LEVEL[0]),
                DBLogItem.level == (LOG_LEVEL[1]),
                DBLogItem.level == (LOG_LEVEL[2])
            ))
        elif level == LOG_LEVEL[3]: # DEBUG
            return s.query(DBLogItem).filter(or_(
                DBLogItem.level == (LOG_LEVEL[0]),
                DBLogItem.level == (LOG_LEVEL[1]),
                DBLogItem.level == (LOG_LEVEL[2]),
                DBLogItem.level == (LOG_LEVEL[3])
            ))

        return None
