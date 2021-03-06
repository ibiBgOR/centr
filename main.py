from flask import Flask, render_template
from flaskext.markdown import Markdown
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_script import Manager
import datetime
import threading
import time
import logging
logging.basicConfig()
import os
import config
from feeditem import Feeditem

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + basedir + '/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.debug = config.DEBUG

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode = True)
database = SQLAlchemy(app)
_logger = logging.getLogger()


migrate = Migrate(app, database)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

Markdown(app)

@manager.command
def runserver():
    app.run(host = '0.0.0.0')

addons = []

@app.template_filter('datetime')
def _jinja2_filter_datetime(date):
    return date.strftime('%d.%m.%Y')

@app.route("/")
def main_route():

    from db import DBFeedItem, DBConnection

    conn = DBConnection()

    feeditems = []
    addonitems = []

    if addons == None:
        _logger.info('No addon loaded...')
        return

    _logger.info(str(len(addons)) + ' addons loaded...')

    for addon in addons:
        if hasattr(addon, 'get_feeds'):
            feeds = getattr(addon, 'get_feeds')()
        else:
            _logger.warn('The addon ' + str(addon) + ' is not supported. Please implement a "get_feeds()" function or contact the developer.')
            continue

        if feeds == None or len(feeds) == 0:
            continue

        addonitems.append(feeds[0].type)

        for feed in feeds:
            if isinstance(feed, Feeditem) or isinstance(feed, DBFeedItem):
                feeditems.append(feed)
            else:
                _logger.warn('The element (' + str(feed) + ') could not be placed on the stream.')

    feeditems.sort(key = lambda element: element.time, reverse = True)

    return render_template('dashboard.html',
        feeditems = feeditems,
        addonitems = addonitems,
        extended = config.SHOW_LINKS,
        date = datetime.datetime.utcnow()
    )

def __load_all_modules():
    '''
    Load all modules from the modules folder.
    '''
    import modules.__init__
    import importlib

    _logger.info('Start to load the modules...')

    for addon in modules.__init__.__all__:
        module = importlib.import_module('.' + addon, 'modules')

        addons.append(module)
        thread = FetchThread(str(addon), module)
        thread.setDaemon(True)
        thread.start()


class FetchThread(threading.Thread):

    _logger = None

    def __init__(self, name, module):
        threading.Thread.__init__(self)
        self.name = name
        self.module = module
        self._logger = logging.getLogger(self.name)

    def run(self):
        if hasattr(self.module, '_load_feeds'):
            while True:
                self.module._load_feeds()
                time.sleep(300) # every 5 minutes
        else:
            self._logger.warning('The addon ' + str(self.name) + ' does not implement the "_load_feeds()" function.')


if __name__ == "__main__":
    __load_all_modules()
    database.create_all()
    manager.run()
