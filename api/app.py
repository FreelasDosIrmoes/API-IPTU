from flask import Flask, json, request, Response
from werkzeug.exceptions import *


app = Flask(__name__)

@app.errorhandler(HTTPException)
def handle_exception(e : HTTPException):
    print(e)
    return json.dumps({
        "code": e.code,
        "description": e.name,
        })

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(f'../storage/{f.filename}.txt')
        return Response(status=201)
    raise MethodNotAllowed()


