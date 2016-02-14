from flask import Flask, render_template
import runtastic
import config

runtastic.fetch_data(config.runtastic['user'], config.runtastic['pass'])

app = Flask(__name__)

@app.route("/")
def main_route():
    feeditems = [{
            'content': 'Runtastic Content',
            'type': 'runtastic',
            'source': 'Runtastic',
            'time': 'Now'
        }]

    return render_template('dashboard.html', feeditems = feeditems, extended = False)

if __name__ == "__main__":
    app.debug = True
    app.run()
