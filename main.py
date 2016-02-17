from flask import Flask, render_template
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_script import Manager
import datetime
import os
import config
from feeditem import Feeditem
import modules.rss
#import db
#from db import DBFeedItem
import modules.__init__
import importlib

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + basedir + '/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.debug = True

addons = []

@app.route("/")
def main_route():

    from db import DBFeedItem, DBLogItem, DBConnection, LOG_LEVEL

    feeditems = []

    if addons == None:
        print 'No addon loaded...'
        return

    for addon in addons:
        feeds = getattr(addon, 'get_feeds')()

        if feeds == None:
            continue

        conn = DBConnection()

        for feed in feeds:
            if isinstance(feed, Feeditem) or isinstance(feed, DBFeedItem):
                feeditems.append(feed)
            else:
                conn.insert_element(
                    DBLogItem('The Element (' + str(feed) + ') could not be placed on the stream.',
                                datetime.datetime.now(),
                                LOG_LEVEL['warn'])
                )

    feeditems.sort(key = lambda r: r.time, reverse = True)

    return render_template('dashboard.html', feeditems = feeditems, extended = False)

def __load_all_modules():
    for addon in modules.__init__.__all__:
        #addons.append(__import__('modules.' + addon, globals))
        addons.append(importlib.import_module('.' + addon, 'modules'))

database = SQLAlchemy(app)
migrate = Migrate(app, database)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode = True)

if __name__ == "__main__":
    __load_all_modules()
    database.create_all()
    manager.run()
