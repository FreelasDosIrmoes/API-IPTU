from flask import *

from werkzeug.exceptions import *
from api.service import *


app = Flask(__name__)
PATH_DEFAULT = "/api/iptu"

@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    return make_response(
        json.dumps({
            "code": e.code,
            "description": e.description,
        }), e.code
    )


@app.route(f"{PATH_DEFAULT}/<int:iptu_code>")
def hello_world(iptu_code : int):
    return make_response({
        "iptu_code": iptu_code
    })


@app.route(f"{PATH_DEFAULT}/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = handling_get_file('file', request)
        f.save(f'../storage/{f.filename}.txt')
        return Response(status=201)
    raise MethodNotAllowed()
