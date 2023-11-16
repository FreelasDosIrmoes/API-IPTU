from flask import Flask
from flask import json
from api.exception.exception import ExceptionResponse, BadRequest, NotFound

app = Flask(__name__)

@app.errorhandler(ExceptionResponse)
def handle_exception(e):
    return json.dumps({
        "code": e.code,
        "description": e.message,
        })

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


