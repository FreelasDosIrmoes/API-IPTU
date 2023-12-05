from werkzeug.exceptions import *
from app import *
import multiprocessing
import time

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

    ok, err = validate_fields(data)
    if not ok:
        return make_response(jsonify({"erro": err})), 400
    owner = data["owner"]
    code = data["code"]
    iptu = Iptu(code=code, status="WAITING")
    db.session.add(iptu)
    db.session.commit()
    dono = Dono(email=owner.get("email", None), numero=owner.get("number", None), iptu=iptu)
    db.session.add(dono)
    db.session.commit()
    return make_response({
        "id": iptu.id,
        "code": iptu.code,
        "dono": {
            "email": dono.email,
            "numero": dono.numero
        }
    }), 201


@app.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['GET'])
def get_iptu(iptu_code: str):
    if request.method != 'GET':
        raise MethodNotAllowed
    iptu = Iptu.query.filter_by(code=iptu_code).first()
    cobrancas = Cobranca.query.filter_by(iptu=iptu).all()

    if iptu is None:
        return jsonify({'erro': 'Codigo de IPTU não encontrado'}), 400

    response_json = {
        'id': iptu.id,
        'name': iptu.name,
        'code': iptu.code,
        'address': iptu.address,
        'status': iptu.status,
        'dono': {
            'nome': iptu.dono.nome if iptu.dono else None,
            'telefone': iptu.dono.telefone if iptu.dono else None
        },
        'cobrancas': [
            {
                'id': cobranca.id,
                'ano': cobranca.ano,
                'cota': cobranca.cota,
                'multa': cobranca.multa,
                'outros': cobranca.outros,
                'total': cobranca.total,
                'pdf': f"/api/iptu/pdf/{cobranca.id}" if cobranca.pdf else None
            }
            for cobranca in cobrancas
        ],
        'updated_at': iptu.updated_at.astimezone().strftime('%d-%m-%Y %H:%M:%S %Z')
    }

    return make_response(response_json)

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
    for iptu in iptus:
        try:
            cobrancasTO = process_extract_data(iptu)
            cobrancas = create_cobranca(cobrancasTO, iptu)
            [db.session.add(cobranca) for cobranca in cobrancas]
            db.session.commit()

        except Exception as e:
            Log(request.url).error_msg(e)
            raise e
        iptu.status = "DONE"
        db.session.commit()
        automation_status.value = 0
    return make_response([{"id": data.id, "total": data.total} for data in cobrancas])
