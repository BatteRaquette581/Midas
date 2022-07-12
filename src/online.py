# in order for uptimerobot to be able to keep the bot up
from flask import Flask
from threading import Thread
app = Flask(__name__)
@app.route("/")
def maintain():
    return '<a href="https://m.youtube.com/watch?v=dQw4w9WgXcQ">Click here!</a>'
def run():
    app.run(host="0.0.0.0", port=8080)
def keep_alive():
    thread = Thread(target=run)
    thread.start()