# app.py
from flask import *
from werkzeug.exceptions import *
from api.service import handling_get_file
from model.model import db, Iptu

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/iptu-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
def hello_world(iptu_code: int):
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


with app.app_context():
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
