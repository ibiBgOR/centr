from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import or_
from sqlalchemy import exc
import datetime
from main import database as db
from feeditem import Feeditem

class DBFeedItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text)
    type = db.Column(db.String(20))
    source = db.Column(db.String(125))
    time = db.Column(db.DateTime)

    __table_args__ = (
        db.UniqueConstraint('content', 'source', name = 'uk_content_source'),
    )

    def __init__(self, content, type, source, time):
        self.content = content
        self.type = type
        self.source = source
        self.time = time

    def __repr__(self):
        return 'DBFeedItem ID: ' + str(self.id)

LOG_LEVEL = {
    'info': 'INFO',
    'warn': 'WARN',
    'error': 'ERROR',
    'debug': 'DEBUG',
}

class DBLogItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    message = db.Column(db.Text)
    time = db.Column(db.DateTime)
    level = db.Column(db.String(5))
    trace = db.Column(db.Text)

    def __init__(self, msg, time, level, trace = None):
        self.message = msg
        self.time = time
        self.level = level
        self.trace = trace

    def __repr__(self):
        return 'DBLogItem ID: ' + str(self.id) + ' Message: ' + str(self.message)

class DBConnection:
    def __init__(self):
        self.session = sessionmaker()

    def insert_element(self, element):
        s = db.session

        if isinstance(element, DBLogItem) or isinstance(element, DBFeedItem):
            try:
                s.add(element)
                s.commit()
            except exc.IntegrityError, e:
                # we expect integrity errors. The reason is that we may try to regularly insert the same element into the database
                # those elements should not be added to the database and we just rollback the transaction and don't log anything
                s.rollback()
            except Exception, e:
                import traceback
                print e
                #self.insert_element(DBLogItem(str(e), datetime.datetime.now(), LOG_LEVEL['error'], traceback.format_exc()))
                s.rollback()
        elif isinstance(element, Feeditem):
            self.insert_element(DBFeedItem(element.content, element.type, element.source, element.time))
        else:
            self.insert_element(DBLogItem(
                'An element could not be inserted into the database, because it is non of the accepted types. (' + type(element) + ')',
                datetime.datetime.now(),
                LOG_LEVEL['warn'],
            ))

    def get_feeds(self, type):
        s = db.session
        return s.query(DBFeedItem).filter(DBFeedItem.type == type).order_by(DBFeedItem.time.desc())

    def get_logs(self, level):
        s = db.session

        if level == None or level == '':
            return s.query(DBLogItem)
        elif level not in LOG_LEVEL:
            return s.query(DBLogItem).filter(DBLogItem.level == (level))
        elif level == LOG_LEVEL['info']:
            return s.query(DBLogItem).filter(DBLogItem.level == (LOG_LEVEL['info']))
        elif level == LOG_LEVEL['warn']:
            return s.query(DBLogItem).filter(or_(
                DBLogItem.level == (LOG_LEVEL['info']),
                DBLogItem.level == (LOG_LEVEL['warn'])
            ))
        elif level == LOG_LEVEL['error']:
            return s.query(DBLogItem).filter(or_(
                DBLogItem.level == (LOG_LEVEL['info']),
                DBLogItem.level == (LOG_LEVEL['warn']),
                DBLogItem.level == (LOG_LEVEL['error'])
            ))
        elif level == LOG_LEVEL.debug:
            return s.query(DBLogItem).filter(or_(
                DBLogItem.level == (LOG_LEVEL['info']),
                DBLogItem.level == (LOG_LEVEL['warn']),
                DBLogItem.level == (LOG_LEVEL['error']),
                DBLogItem.level == (LOG_LEVEL['debug'])
            ))

        return None
