import sqlalchemy.exc
from werkzeug.exceptions import *
from app import *

PATH_DEFAULT = "/api/iptu"


@app_flask.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    return make_response(
        json.dumps({
            "code": e.code,
            "description": e.description,
        }), e.code
    )


@app_flask.route(f"{PATH_DEFAULT}/", methods=['POST'])
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


@app_flask.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['PUT'])
def update_iptu(iptu_code: str):
    if request.method != 'PUT':
        raise MethodNotAllowed

    data = request.get_json()
    ok, err = validate_fields_put(data)
    if not ok:
        return make_response(jsonify({"errors": err})), 400

    iptu = Iptu.query.filter_by(code=iptu_code).first()

    if iptu is None:
        return jsonify({'erro': 'Codigo de IPTU não encontrado'}), 400

    iptu.code = data['code']
    iptu.name = data['name']
    iptu.dono.email = data['owner']['email']
    iptu.dono.numero = data['owner']['number']
    iptu.dono.nome = data['owner']['name']
    try:
        db.session.commit()
    except Exception as e:
        raise BadRequest(str(e))

    return make_response(build_request(iptu, iptu.cobranca)), 200


@app_flask.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['GET'])
def get_iptu(iptu_code: str):
    if request.method != 'GET':
        raise MethodNotAllowed
    iptu = Iptu.query.filter_by(code=iptu_code).first()
    cobrancas = Cobranca.query.filter_by(iptu=iptu).all()

    if iptu is None:
        return jsonify({'erro': 'Codigo de IPTU não encontrado'}), 400

    return make_response(build_request(iptu, cobrancas))


@app_flask.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['DELETE'])
def delete_iptu(iptu_code: str):
    if request.method != 'DELETE':
        raise MethodNotAllowed
    iptu = Iptu.query.filter_by(code=iptu_code).first()

    if iptu is None:
        return jsonify({'erro': 'Codigo de IPTU não encontrado'}), 400

    db.session.delete(iptu)
    db.session.commit()
    return make_response({'message': 'IPTU deletado com sucesso'})


@app_flask.route(f"{PATH_DEFAULT}/pdf/<int:cobranca_id>")
def get_pdf(cobranca_id):
    cobranca = Cobranca.query.get(cobranca_id)
    if cobranca is None:
        return jsonify({'erro': 'Cobrança não encontrado'}), 400
    pdf_data = cobranca.pdf

    return pdf_data, 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=arquivo.pdf'}



