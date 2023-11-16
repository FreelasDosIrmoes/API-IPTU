from flask import *
from werkzeug.exceptions import *


app = Flask(__name__)

@app.errorhandler(HTTPException)
def handle_exception(e : HTTPException):
    return make_response(json.dumps({
            "code": e.code,
            "description": e.description,
        }), e.code)
                

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = handling_get_file('file', request)
        f.save(f'../storage/{f.filename}.txt')
        return Response(status=201)
    raise MethodNotAllowed()

def handling_get_file(filename : str, request : Request):
    f = None
    try:
        f = request.files[filename]
        return f
    except Exception as e:
        raise BadRequest('file with name "file" is required')