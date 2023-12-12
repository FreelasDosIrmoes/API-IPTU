import sqlalchemy.exc
from werkzeug.exceptions import *
from app import *
from app.service import validate_fields_put, send_email_and_wpp, send_only_email, send_only_wpp
from app.service import validate_fields_post
from app.service import build_iptu_and_dono
from app.service import build_request
from app.model.model import *
from flask import jsonify
from flask import request
from flask import make_response
from flask import json
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
    """
        Save IPTU
        ---
        tags:
              - IPTU
        parameters:
          - name: data
            in: body
            required: true
            schema:
              type: object
              properties:
                code:
                  type: string
                  description: IPTU code
                  example: "12345678"
                name:
                  type: string
                  description: IPTU name
                  example: "Teste"
                send:
                    type: boolean
                    description: Send email and wpp
                    example: true
                owner:
                  type: object
                  properties:
                    name:
                      type: string
                      description: Owner name
                      example: Teste
                    email:
                      type: string
                      description: Owner email
                      example:
                    number:
                      type: string
                      description: Owner number
                      example: "5585912345678"
        responses:
          201:
            description: Successful operation
        """
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
    """
     Update IPTU by code
     ---
     tags:
              - IPTU
     parameters:
       - name: iptu_code
         in: path
         type: string
         required: true
         description: IPTU code
       - name: data
         in: body
         required: true
         schema:
           type: object
           properties:
             code:
               type: string
               description: New code for the IPTU
             name:
               type: string
               description: New name for the IPTU
             owner:
               type: object
               properties:
                 email:
                   type: string
                   description: Email of the owner
                 number:
                   type: string
                   description: Number of the owner
                 name:
                   type: string
                   description: Name of the owner
     responses:
       200:
         description: Successful operation
    """
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
    if iptu.dono is not None:
        iptu.dono.email = data['owner']['email']
        iptu.dono.numero = data['owner']['number']
        iptu.dono.nome = data['owner']['name']
    else:
        dono = Dono(email=data['owner']['email'], numero=data['owner']['number'], nome=data['owner']['name'],
                    iptu=iptu)
        db.session.add(dono)
    iptu.status = "WAITING"

    try:
        db.session.commit()
    except Exception as e:
        raise BadRequest(str(e))

    return make_response(build_request(iptu, iptu.cobranca)), 200


@app_flask.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['GET'])
def get_iptu(iptu_code: str):
    """
        Get IPTU by code
        ---
        tags:
              - IPTU
        parameters:
          - name: iptu_code
            in: path
            type: string
            required: true
            description: IPTU code
        responses:
          200:
            description: Successful operation
            schema:
              type: object
              properties:
                id:
                  type: integer
                  description: ID of the IPTU
                code:
                  type: string
                  description: Code of the IPTU
                name:
                  type: string
                  description: Name of the IPTU
                dono:
                  type: object
                  properties:
                    email:
                      type: string
                      description: Email of the owner
                    numero:
                      type: string
                      description: Number of the owner
        """
    if request.method != 'GET':
        raise MethodNotAllowed
    iptu = Iptu.query.filter_by(code=iptu_code).first()
    cobrancas = Cobranca.query.filter_by(iptu=iptu).all()

    if iptu is None:
        return jsonify({'erro': 'Codigo de IPTU não encontrado'}), 400

    return make_response(build_request(iptu, cobrancas))


@app_flask.route(f"{PATH_DEFAULT}/<iptu_code>", methods=['DELETE'])
def delete_iptu(iptu_code: str):
    """
        Delete IPTU by code
        ---

        tags:
              - IPTU
        parameters:
          - name: iptu_code
            in: path
            type: string
            required: true
            description: IPTU code
        responses:
          200:
            description: Successful operation
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Deletion success message
        """
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
    """
        Get PDF for a specific Cobranca
        ---
        tags:
              - Cobranças
        parameters:
          - name: cobranca_id
            in: path
            type: integer
            required: true
            description: ID of the Cobranca
        responses:
          200:
            description: Successful operation
            content:
              application/pdf:
                schema:
                  type: file
            headers:
              Content-Type:
                type: string
                description: Mime type of the file (application/pdf)
              Content-Disposition:
                type: string
                description: Attachment with the filename (arquivo.pdf)
        400:
          description: Cobrança not found
        """
    cobranca = Cobranca.query.get(cobranca_id)
    if cobranca is None:
        return jsonify({'erro': 'Cobrança não encontrado'}), 400
    pdf_data = cobranca.pdf

    return pdf_data, 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=arquivo.pdf'}


@app_flask.route(f"{PATH_DEFAULT}/<iptu_code>/inconsistent", methods=['PATCH'])
def update_inconsistent(iptu_code):
    """
        Update IPTU inconsistency status by code
        ---
        tags:
              - IPTU
        parameters:
          - name: iptu_code
            in: path
            type: string
            required: true
            description: IPTU code
        responses:
          200:
            description: Successful operation
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Update success message
        400:
          description: IPTU not found
        """
    if request.method != 'PATCH':
        raise MethodNotAllowed
    iptu = Iptu.query.filter_by(code=iptu_code).first()
    if iptu is None:
        return jsonify({'erro': 'Codigo de IPTU não encontrado'}), 400
    iptu.inconsistent = False
    iptu.status = 'WAITING'
    try:
        db.session.commit()
    except Exception as e:
        raise BadRequest(str(e))
    return make_response({'message': 'IPTU atualizado com sucesso'}), 200


@app_flask.route(f"{PATH_DEFAULT}/", methods=['GET'])
def get_all_iptus():
    """
            Retorna todos os registros de IPTU.

            ---
            tags:
              - IPTU
            responses:
              200:
                description: Sucesso. Retorna uma lista de objetos IPTU.
              405:
                description: Método não permitido. Apenas o método GET é permitido.
            """
    if request.method != 'GET':
        raise MethodNotAllowed
    iptus = Iptu.query.all()
    return make_response(jsonify(
        [{"id": iptu.id,
          "code": iptu.code,
          "name": iptu.name,
          "total": sum([cobranca.total for cobranca in iptu.cobranca]) if iptu.cobranca else 0,
          "status": iptu.status,
          "address": iptu.address,
          "updated_at": iptu.updated_at.astimezone().strftime('%d-%m-%Y %H:%M:%S %Z'),
          "inconsistent": iptu.inconsistent,
          } for iptu in iptus])), 200


@app_flask.route(f"{PATH_DEFAULT}/send-wpp/<cobranca_id>", methods=['POST'])
def send_wpp(cobranca_id):
    """
            Envia uma cobrança via WhatsApp.

            ---
            tags:
              - Cobranças
            parameters:
              - name: cobranca_id
                in: path
                type: string
                required: true
                description: ID da cobrança.
            responses:
              200:
                description: Sucesso. Retorna um objeto com a mensagem.
              400:
                description: Erro. Retorna um objeto com a mensagem de erro.
            """
    if request.method != 'POST':
        raise MethodNotAllowed
    if cobranca_id is None:
        return jsonify({'erro': 'Cobrança não encontrada'}), 400
    cobranca = Cobranca.query.get(cobranca_id)

    if cobranca is None:
        return jsonify({'erro': 'Cobrança não encontrada'}), 400

    iptu = Iptu.query.get(cobranca.iptu_id)

    if iptu is None:
        return jsonify({'erro': 'IPTU não encontrado'}), 400

    send_only_wpp(iptu, cobranca, iptu.dono)

    return make_response({'message': 'Email enviado com sucesso'}), 200


@app_flask.route(f"{PATH_DEFAULT}/send-email/<cobranca_id>", methods=['POST'])
def send_email(cobranca_id):
    """
            Envia uma cobrança por e-mail.

            ---
            tags:
              - Cobranças
            parameters:
              - name: cobranca_id
                in: path
                type: string
                required: true
                description: ID da cobrança.
            responses:
              200:
                description: Sucesso. Retorna um objeto com a mensagem.
              400:
                description: Erro. Retorna um objeto com a mensagem de erro.
            """
    if request.method != 'POST':
        raise MethodNotAllowed
    if cobranca_id is None:
        return jsonify({'erro': 'Cobrança não encontrada'}), 400
    cobranca = Cobranca.query.get(cobranca_id)

    if cobranca is None:
        return jsonify({'erro': 'Cobrança não encontrada'}), 400

    iptu = Iptu.query.get(cobranca.iptu_id)

    if iptu is None:
        return jsonify({'erro': 'IPTU não encontrado'}), 400

    send_only_email(iptu, cobranca, iptu.dono)

    return make_response({'message': 'Email enviado com sucesso'}), 200