from flask import Flask, render_template
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
