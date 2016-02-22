from flask import Flask, render_template
from flaskext.markdown import Markdown
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_script import Manager
import datetime
import os
import config
from feeditem import Feeditem

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + basedir + '/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.debug = True

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode = True)
database = SQLAlchemy(app)

migrate = Migrate(app, database)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

Markdown(app)

@manager.command
def runserver():
    app.run(host = '0.0.0.0')

addons = []

@app.route("/")
def main_route():

    from db import DBFeedItem, DBLogItem, DBConnection, LOG_LEVEL

    conn = DBConnection()

    feeditems = []
    addonitems = []

    if addons == None:
        print 'No addon loaded...'
        return

    for addon in addons:
        if hasattr(addon, 'get_feeds'):
            feeds = getattr(addon, 'get_feeds')()
        else:
            conn.insert_element(
                DBLogItem('The addon ' + str(addon) + ' is not supported. Please implement a "get_feeds()" function or contact the developer.',
                            datetime.datetime.now(),
                            LOG_LEVEL['warn']
                )
            )
            feeds = None

        if feeds == None or len(feeds) == 0:
            continue

        addonitems.append(feeds[0].type)

        for feed in feeds:
            if isinstance(feed, Feeditem) or isinstance(feed, DBFeedItem):
                feeditems.append(feed)
            else:
                conn.insert_element(
                    DBLogItem('The Element (' + str(feed) + ') could not be placed on the stream.',
                                datetime.datetime.now(),
                                LOG_LEVEL['warn']
                    )
                )

    feeditems.sort(key = lambda element: element.time, reverse = True)

    return render_template('dashboard.html', feeditems = feeditems, addonitems = addonitems, extended = False)

def __load_all_modules():
    '''
    Load all modules from the modules folder.
    '''
    import modules.__init__
    import importlib

    for addon in modules.__init__.__all__:
        addons.append(importlib.import_module('.' + addon, 'modules'))

if __name__ == "__main__":
    __load_all_modules()
    database.create_all()
    manager.run()
