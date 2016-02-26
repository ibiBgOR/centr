from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import or_
from sqlalchemy import exc
import datetime
import logging
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

class DBConnection:

    _logger = logging.getLogger('DBConnection')

    def __init__(self):
        self.session = sessionmaker()

    def insert_element(self, element):
        s = db.session

        if isinstance(element, DBFeedItem):
            try:
                s.add(element)
                s.commit()
            except exc.IntegrityError, e:
                # we expect integrity errors. The reason is that we may try to regularly insert the same element into the database
                # those elements should not be added to the database and we just rollback the transaction and don't log anything
                s.rollback()
            except Exception, e:
                self._logger.error(str(e))
                s.rollback()
        elif isinstance(element, Feeditem):
            self.insert_element(DBFeedItem(element.content, element.type, element.source, element.time))
        else:
            self._logger.warning('An element could not be inserted into the database, because it is non of the accepted types. (' + type(element) + ')')

    def get_feeds(self, type):
        s = db.session
        return s.query(DBFeedItem).filter(DBFeedItem.type == type).order_by(DBFeedItem.time.desc())
