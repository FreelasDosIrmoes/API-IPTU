from werkzeug.exceptions import *
from app import *

PATH_DEFAULT = "/api/iptu"


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    return make_response(
        json.dumps({
            "code": e.code,
            "description": e.description,
        }), e.code
    )


@app.route(f"{PATH_DEFAULT}/<int:iptu_code>", methods=['POST'])
def save_iptucode(iptu_code: int):
    if request.method != "POST":
        raise MethodNotAllowed
    db.session.add(IptuTemp(code=iptu_code, status="WAITING"))
    db.session.commit()
    return make_response({
        "iptu_code": iptu_code,
        "status": "WAITING"
    })


@app.route(f"{PATH_DEFAULT}/trigger", methods=['POST'])
def trigger_process():
    if request.method != 'POST':
        raise MethodNotAllowed
    temps = IptuTemp.query.all()
    for iptu in temps:
        # iptuDB = Iptu(code=iptu.code)
        # db.session.add(iptuDB)
        # db.session.commit()
        # print(iptuDB.id)
        try:
            cobrancasTO = process_extract_data(iptu)
            cobrancas = create_cobranca(cobrancasTO)
            [db.session.add(cobranca) for cobranca in cobrancas]
            db.session.commit()
        except Exception as e:
            Log(request.url).error_msg(e)
            raise e

    return make_response([{"code": data.code, "status": data.status} for data in temps])

