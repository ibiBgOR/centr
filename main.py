from flask import Flask, render_template
import config
from feeditem import Feeditem
import rss

app = Flask(__name__)

@app.route("/")
def main_route():
    feeditems = []
    feeditems.extend(rss.get_feeds(rss.rssfeeds))

    return render_template('dashboard.html', feeditems = feeditems, extended = False)

if __name__ == "__main__":
    app.debug = True
    app.run()
