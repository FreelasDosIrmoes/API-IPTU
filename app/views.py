import sqlalchemy.exc
from werkzeug.exceptions import *
from app import *
import multiprocessing

PATH_DEFAULT = "/api/iptu"


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    return make_response(
        json.dumps({
            "code": e.code,
            "description": e.description,
        }), e.code
    )


@app.route(f"{PATH_DEFAULT}/", methods=['POST'])
def save_iptucode():
    if request.method != "POST":
        raise MethodNotAllowed
    data = request.get_json()

    ok, err = validate_fields_post(data)
    if not ok:
        return make_response(jsonify({"erro": err})), 400

    iptu, dono = build_iptu_and_dono(data)

    try:
        db.session.add(iptu)
        db.session.add(dono)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        raise BadRequest(e.orig.args[0])

    return make_response({
        "id": iptu.id,
        "code": iptu.code,
        "name": iptu.name,
        "dono": {
            "email": dono.email,
            "numero": dono.numero
        }
    }), 201


@app.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['PUT'])
def update_iptu(iptu_code: str):
    if request.method != 'PUT':
        raise MethodNotAllowed
    data = request.get_json()
    iptu = Iptu.query.filter_by(code=iptu_code).first()
    if iptu is None:
        return jsonify({'erro': 'Codigo de IPTU não encontrado'}), 400
    iptu.name = data['name']
    iptu.dono.email = data['owner']['email']
    iptu.dono.numero = data['owner']['number']
    db.session.commit()
    return make_response({
        "id": iptu.id,
        "code": iptu.code,
        "name": iptu.name,
        "dono": {
            "email": iptu.dono.email,
            "numero": iptu.dono.numero
        }
    }), 200


@app.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['GET'])
def get_iptu(iptu_code: str):
    if request.method != 'GET':
        raise MethodNotAllowed
    iptu = Iptu.query.filter_by(code=iptu_code).first()
    cobrancas = Cobranca.query.filter_by(iptu=iptu).all()

    if iptu is None:
        return jsonify({'erro': 'Codigo de IPTU não encontrado'}), 400

    return make_response(build_request(iptu, cobrancas))


@app.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['DELETE'])
def delete_iptu(iptu_code: str):
    if request.method != 'DELETE':
        raise MethodNotAllowed
    iptu = Iptu.query.filter_by(code=iptu_code).first()
    if iptu is None:
        return jsonify({'erro': 'Codigo de IPTU não encontrado'}), 400
    db.session.delete(iptu)
    db.session.commit()
    return make_response({'message': 'IPTU deletado com sucesso'})


@app.route(f"{PATH_DEFAULT}/pdf/<int:cobranca_id>")
def get_pdf(cobranca_id):
    cobranca = Cobranca.query.get(cobranca_id)
    if cobranca is None:
        return jsonify({'erro': 'Cobrança não encontrado'}), 400
    pdf_data = cobranca.pdf

    return pdf_data, 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=arquivo.pdf'}


automation_status = multiprocessing.Value("i", 0)


@app.route(f"{PATH_DEFAULT}/trigger", methods=['POST'])
def trigger_process():
    if request.method != 'POST':
        raise MethodNotAllowed
    if automation_status.value == 1:
        return {"message": "Automaçao rodando"}, 409
    automation_status.value = 1
    iptus = Iptu.query.filter_by(status="WAITING").all()
    cobrancas = []
    for iptu in iptus:
        try:
            cobrancas_to = process_extract_data(iptu)
            cobrancas = create_cobranca(cobrancas_to, iptu)
            [db.session.add(cobranca) for cobranca in cobrancas]
            db.session.commit()

        except Exception as e:
            Log(request.url).error_msg(e)
            raise e
        iptu.status = "DONE"
        db.session.commit()
        automation_status.value = 0
    return make_response([{"id": data.id, "total": data.total} for data in cobrancas])
