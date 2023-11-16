from flask import Flask
from flask import json
from werkzeug.exceptions import *


app = Flask(__name__)

@app.errorhandler(HTTPException)
def handle_exception(e):
    print(e)
    return json.dumps({
        "code": e.code,
        "description": "teste",
        })

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


