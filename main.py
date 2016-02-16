from flask import Flask, render_template
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
import config
from feeditem import Feeditem
from modules import rss
import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.debug = True

@app.route("/")
def main_route():
    feeditems = []
    feeditems.extend(rss.get_feeds(rss.rssfeeds))

    feeditems.sort(key = lambda r: r.time, reverse = True)

    return render_template('dashboard.html', feeditems = feeditems, extended = False)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
