from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def main_route():
    return render_template('dashboard.html', feeditems = [
        {
            'content': 'Runtastic Content',
            'type': 'runtastic',
            'source': 'Runtastic',
            'time': 'Now'
        },
        {
            'content': 'Runtastic Content',
            'type': 'runtastic',
            'source': 'Runtastic',
            'time': 'Now'
        },
        {
            'content': 'Runtastic Content',
            'type': 'runtastic',
            'source': 'Runtastic',
            'time': 'Now'
        },
        {
            'content': 'Runtastic Content',
            'type': 'runtastic',
            'source': 'Runtastic',
            'time': 'Now'
        },
        {
            'content': 'Runtastic Content',
            'type': 'runtastic',
            'source': 'Runtastic',
            'time': 'Now'
        },
        {
            'content': 'RSS Content',
            'type': 'rss',
            'source': 'RSS Source',
            'time': 'Today 15:12'
        }
    ], extended=False)

if __name__ == "__main__":
    app.debug = True
    app.run()
