from werkzeug.exceptions import *
from app import *
import multiprocessing
import time

PATH_DEFAULT = "/api/iptu"


@app_flask.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    return make_response(
        json.dumps({
            "code": e.code,
            "description": e.description,
        }), e.code
    )


@app_flask.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['POST', 'GET'])
def save_iptucode(iptu_code: str):
    if request.method == "POST":
        db.session.add(Iptu(code=iptu_code, status="WAITING"))
        db.session.commit()
        return make_response({
            "iptu_code": iptu_code,
            "status": "WAITING"
        })
    if request.method == "GET":
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


@app_flask.route(f"{PATH_DEFAULT}/pdf/<int:cobranca_id>")
def get_pdf(cobranca_id):
    cobranca = Cobranca.query.get(cobranca_id)
    if cobranca is None:
        return jsonify({'erro': 'Cobrança não encontrado'}), 400
    pdf_data = cobranca.pdf

    return pdf_data, 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=arquivo.pdf'}


automation_status = multiprocessing.Value("i", 0)


@app_flask.route(f"{PATH_DEFAULT}/trigger", methods=['POST'])
def trigger_process():
    if request.method != 'POST':
        raise MethodNotAllowed
    if automation_status.value == 1:
        return {"message": "Automaçao rodando"}, 409
    automation_status.value = 1
    iptus = query_to_get_iptu_late(app_flask)
    for iptu in iptus:
        try:
            iptu = Iptu.query.get(iptu.id)
            cobrancas_to = process_extract_data(iptu)
            if len(cobrancas_to) == 0:
                print("AUTOMAÇAO RETORNOU UMA LISTA VAZIA")
                continue
            cobrancas = create_cobranca(cobrancas_to, iptu)

            cobrancas_db = Cobranca.query.filter_by(iptu=iptu).all()

            [db.session.delete(cobranca_db) for cobranca_db in cobrancas_db]

            [db.session.add(cobranca) for cobranca in cobrancas]

            iptu.status = "DONE"
            iptu.updated_at = datetime.now()
            db.session.commit()

        except Exception as e:
            Log(request.url).error_msg(e)
            raise e
    automation_status.value = 0
    return {"message": "Automaçao finalizada"}, 201
