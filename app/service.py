from datetime import datetime
import json
import locale
from flask import request
from sqlalchemy.engine import Engine
from app.model.model import Iptu, Cobranca, Dono
from app import db, API_MSG
from sqlalchemy import create_engine, text
from time import sleep
import requests
from werkzeug.exceptions import *
import re
from datetime import datetime

def criar_iptu_com_api(data):
    codigo = data['code']
    response_json_exercicio_1 = pegar_dados_info_api(codigo, "1")
    if response_json_exercicio_1['code'] != 200:
        raise BadRequest(f"Erro ao buscar dados do IPTU {codigo}. Erro: {response_json_exercicio_1['code_message']}")
    dados_iptu = response_json_exercicio_1['data'][0]
    endereco = dados_iptu['endereco']
    nome_razao_social = dados_iptu['nome_razao_social']

    
    iptu = Iptu()
    iptu.code = codigo
    iptu.name = nome_razao_social
    iptu.status = "DONE"
    iptu.address = endereco
    iptu.updated_at = datetime.now()
    iptu.inconsistent = False if nome_razao_social == data['name'] else True
    iptu.send = data['send']

    dono = Dono()
    dono.email = data['owner']['email']
    dono.numero = data['owner']['number']
    dono.nome = data['owner']['name']
    dono.iptu = iptu

    debitos: list = dados_iptu['debitos']
    response_json_exercicio_2 = pegar_dados_info_api(codigo, "2")
    debitos += response_json_exercicio_2['data'][0]['debitos'] if response_json_exercicio_2['code'] == 200 else []

    cobrancas = list()
    for debito in debitos:
        cobranca = Cobranca()
        cobranca.ano = debito['ano']
        cobranca.cota = debito['cota']
        cobranca.multa = debito['normalizado_multa']
        cobranca.outros = debito['normalizado_outros']
        cobranca.total = debito['normalizado_valor_total']
        # cobranca.status_boleto = calcular_status_cobranca(cobranca)
        cobranca.iptu = iptu
        cobranca.updated_at = datetime.now()
        cobranca.pdf = debito['guia_pdf_url']
        cobrancas.append(cobranca)

    return iptu, dono, cobrancas

def pegar_dados_info_api(codigo, exercicio):
    # url = 'https://api.infosimples.com/api/v2/consultas/sefaz/df/iptu'
    # args = {
    # "inscricao_imovel": codigo,
    # "exercicio":        exercicio,
    # "token":            "RmqPUVXMZ9x09TbWZRN48fD4ryKog8HS9UUR1CB4",
    # "timeout":          300
    # }

    # response = requests.post(url, args)
    # response_json = response.json()
    # response.close()

    # if response_json['code'] != 200 and response_json['code'] not in range(600, 799):
    #     raise InternalServerError(f"Erro ao buscar dados do IPTU {codigo}. Erro: {response_json['message']}")

    return {'code': 200, 'code_message': 'A requisição foi processada com sucesso.', 'header': {'api_version': 'v2', 'api_version_full': '2.2.16-20240216160655', 'product': 'Consultas', 'service': 'sefaz/df/iptu', 'parameters': {'exercicio': 1, 'inscricao_imovel': '48517852'}, 'client_name': 'Arthur Silva Queiroz', 'token_name': 'Arthur Silva Queiroz', 'billable': True, 'price': '0.2', 'requested_at': '2024-02-18T16:21:48.000-03:00', 'elapsed_time_in_milliseconds': 6112, 'remote_ip': '179.67.250.214', 'signature': 'U2FsdGVkX1/fSfJJ0DhHq8XAOlHne0aHqeddvSG8TKxbEt4IMrzBl50CnkmcG2HIh/hKRcDYw1fOA+ucXFKVQQ=='}, 'data_count': 1, 'data': [{'debitos': [{'ano': '2024', 'cota': '00 IPTU / TLP', 'valor': '805,38', 'multa': '0,00', 'juros': '0,00', 'outros': '0,00', 'valor_total': '805,38', 'normalizado_valor_total': 805.38, 'normalizado_outros': 0.0, 'normalizado_juros': 0.0, 'normalizado_multa': 0.0, 'normalizado_valor': 805.38, 'guia_pdf_url': 'https://storage.googleapis.com/infosimples-api-tmp/20240218162144/r2-J2PjV5kg1BIk39k0CPwvDzY2bYoge/0d53608bf709c0bd3c29975dc4827bfe.pdf'}, {'ano': '2024', 'cota': '01 IPTU / TLP', 'valor': '134,22', 'multa': '0,00', 'juros': '0,00', 'outros': '0,00', 'valor_total': '134,22', 'normalizado_valor_total': 134.22, 'normalizado_outros': 0.0, 'normalizado_juros': 0.0, 'normalizado_multa': 0.0, 'normalizado_valor': 134.22, 'guia_pdf_url': 'https://storage.googleapis.com/infosimples-api-tmp/20240218162144/KpnjB-B7tuO4ykybdxs1GAa2uoz-ARn7/2e1345721a5c785b748f8ecad296706c.pdf'}, {'ano': '2024', 'cota': '02 IPTU / TLP', 'valor': '134,22', 'multa': '0,00', 'juros': '0,00', 'outros': '0,00', 'valor_total': '134,22', 'normalizado_valor_total': 134.22, 'normalizado_outros': 0.0, 'normalizado_juros': 0.0, 'normalizado_multa': 0.0, 'normalizado_valor': 134.22, 'guia_pdf_url': 'https://storage.googleapis.com/infosimples-api-tmp/20240218162145/hcEfafzKUAXN-tIDf3FAc0kmN0EYeJYr/0d6e70f46a576b4621d4c0470283146f.pdf'}, {'ano': '2024', 'cota': '03 IPTU / TLP', 'valor': '134,22', 'multa': '0,00', 'juros': '0,00', 'outros': '0,00', 'valor_total': '134,22', 'normalizado_valor_total': 134.22, 'normalizado_outros': 0.0, 'normalizado_juros': 0.0, 'normalizado_multa': 0.0, 'normalizado_valor': 134.22, 'guia_pdf_url': 'https://storage.googleapis.com/infosimples-api-tmp/20240218162146/m6dkjXZc1rq6VvghB3relfguTV7EXBCv/19e3785bca5dfe6675347e7af086e032.pdf'}, {'ano': '2024', 'cota': '04 IPTU / TLP', 'valor': '134,22', 'multa': '0,00', 'juros': '0,00', 'outros': '0,00', 'valor_total': '134,22', 'normalizado_valor_total': 134.22, 'normalizado_outros': 0.0, 'normalizado_juros': 0.0, 'normalizado_multa': 0.0, 'normalizado_valor': 134.22, 'guia_pdf_url': 'https://storage.googleapis.com/infosimples-api-tmp/20240218162147/FMcKuT_fY_rznLHSsUGs_AjHOpms-X-z/5d85a174b20cb316e81ef86152cf8417.pdf'}, {'ano': '2024', 'cota': '05 IPTU / TLP', 'valor': '134,22', 'multa': '0,00', 'juros': '0,00', 'outros': '0,00', 'valor_total': '134,22', 'normalizado_valor_total': 134.22, 'normalizado_outros': 0.0, 'normalizado_juros': 0.0, 'normalizado_multa': 0.0, 'normalizado_valor': 134.22, 'guia_pdf_url': 'https://storage.googleapis.com/infosimples-api-tmp/20240218162147/H5jPkwsi90xbMPR7KqXm1YGrpZdHZDSb/fbf0bdf0532ec60b88d5cd450adc811a.pdf'}, {'ano': '2024', 'cota': '06 IPTU / TLP', 'valor': '134,28', 'multa': '0,00', 'juros': '0,00', 'outros': '0,00', 'valor_total': '134,28', 'normalizado_valor_total': 134.28, 'normalizado_outros': 0.0, 'normalizado_juros': 0.0, 'normalizado_multa': 0.0, 'normalizado_valor': 134.28, 'guia_pdf_url': 'https://storage.googleapis.com/infosimples-api-tmp/20240218162148/AuCA-35qy384m5eJf37VnRhGsa-zwkEZ/82f8f38cf0547cba7de35bd3458c6d3f.pdf'}], 'endereco': 'SRIA QE 38 BL C AP 104', 'inscricao': '48517852', 'nome_razao_social': 'BRAZILIAN SECURITIES COMPANHIA DE SECURITIZACAO', 'site_receipt': None}], 'errors': [], 'site_receipts': []}

def calcular_status_cobranca(cobranca):
    if bool(re.search(r'\d', cobrancas.cota)):
        meses = {'01': 5, '02': 6, '03': 7, '04': 8, '05': 9, '06': 10}
        mes = cobranca.cota[:2]
        try:
            data_cobranca = f'01/{meses[mes]}/{cobranca.ano}'
            data_cobranca = datetime.strptime(data_cobranca, '%d/%m/%Y')
            if data_cobranca.year == datetime.now().year:
                cobranca.status_pagamento = 'PENDENTE'
            else:
                cobranca.status_pagamento = 'SEM DÉBITOS'
        except:
            cobranca.status_pagamento = 'SEM DÉBITOS'

def process_extract_data(iptu, dono):
    start_process = datetime.now()
    robot = Automation()
    previous, is_inconsistent_previous, name, address = robot.process_flux_previous_years(iptu.code, iptu.name)
    current, is_inconsistent_current, name, address = robot.process_flux_current_year(iptu.code, iptu.name)
    finish_process = datetime.now()
    Log().time_all_process(finish_process - start_process)
    previous = previous if previous else []
    current = current if current else []
    return previous + current, is_inconsistent_current or is_inconsistent_previous, name, address

def contem_cobranca_pendente(iptu : Iptu):
    for cobranca in iptu.cobranca:
        if cobranca.status_boleto == "PENDENTE":
            return True
    return False


def create_cobrancas(data, iptu):
    list = []
    for d in data:
        cobranca = dict_to_cobranca(d, iptu)
        list.append(cobranca)
    return list


def dict_to_cobranca(cobranca_dict, iptu):
    ano = int(cobranca_dict['ano'])
    multa = format_number(cobranca_dict['multa'])
    outros = format_number(cobranca_dict['outros'])
    total = format_number(cobranca_dict['total'])
    cota = cobranca_dict['cota']
    pdf_data = cobranca_dict['pdf_byte']
    status_boleto = "PENDENTE" if cobranca_dict['a_vencer'] else "PAGO"
    return (ano, cota, multa, outros, total, iptu, pdf_data, status_boleto)


def format_number(value):
    value = value.replace(',', '.')
    value = value.replace('.', '')
    value = value[0:len(value)-2] + '.' + value[len(value)-2:len(value)]
    return float(value)


def insert_cobrancas(connection, cobrancas):
    for cobranca in cobrancas:
        query = text(
            '''INSERT INTO cobranca (ano, cota, multa, outros, total, iptu_id, pdf, status_boleto, updated_at)
            VALUES (
                :ano,
                :cota,
                :multa,
                :outros,
                :total,
                :iptu_id,
                :pdf,
                :status_boleto,
                now()
                )'''
        )
        connection.execute(query, {"ano": cobranca[0], "cota": cobranca[1], "multa": cobranca[2], "outros": cobranca[3],
                                   "total": cobranca[4], "iptu_id": cobranca[5].id, "pdf": cobranca[6], "status_boleto": cobranca[7]})


def validate_fields_post(data):
    errors = []
    if 'code' not in data:
        errors.append("Campo 'code' não informado")
    if 'owner' not in data:
        errors.append("Campo 'owner' não informado")
    if 'email' not in data['owner']:
        errors.append("Campo 'owner.email' não informado")
    if 'number' not in data['owner']:
        errors.append("Campo 'owner.number' não informado")
    if 'name' not in data:
        errors.append("Campo 'name' não informado")
    if 'name' not in data['owner']:
        errors.append("Campo 'owner.name' não informado")
    return len(errors) == 0, errors


def build_iptu_and_dono(data):
    iptu = Iptu(code=data['code'], name=data['name'], status="WAITING", send= data['send'] if 'send' in data else False)
    dono = Dono(email=data['owner']['email'], numero=data['owner']['number'], nome=data['owner']['name'], iptu=iptu)
    return iptu, dono


def validate_fields_put(data):
    errors = []
    if 'name' not in data:
        errors.append("Campo 'name' não informado")
    if 'code' not in data:
        errors.append("Campo 'code' não informado")
    if 'owner' not in data:
        errors.append("Campo 'owner' não informado")
    if 'email' not in data['owner']:
        errors.append("Campo 'email' não informado")
    if 'number' not in data['owner']:
        errors.append("Campo 'number' não informado")
    if 'name' not in data['owner']:
        errors.append("Campo 'name' não informado")
    return len(errors) == 0, errors


def build_request(iptu, cobrancas):
    return {
        'id': iptu.id,
        'name': iptu.name,
        'code': iptu.code,
        'status': iptu.status,
        'inconsistent': iptu.inconsistent,
        'status_payment': 'A VENCER' if contem_cobranca_pendente(iptu) else 'SEM DÉBITOS',
        'dono': {
            'nome': iptu.dono.nome if iptu.dono else None,
            'email': iptu.dono.email if iptu.dono else None,
            'numero': iptu.dono.numero if iptu.dono else None
        },
        'cobrancas': [
            {
                'id': cobranca.id,
                'ano': cobranca.ano,
                'cota': cobranca.cota,
                'multa': cobranca.multa,
                'outros': cobranca.outros,
                'total': cobranca.total,
                'status_boleto': cobranca.status_boleto,
                'pdf': f"/api/iptu/pdf/{cobranca.id}" if cobranca.pdf else None
            }
            for cobranca in cobrancas
        ],
        'address': iptu.address,
        'total': sum([cobranca.total for cobranca in cobrancas]) if cobrancas else 0,
        'updated_at': iptu.updated_at.astimezone().strftime('%d-%m-%Y %H:%M:%S %Z')
    }


def get_engine(app_flask):
    with app_flask.app_context():
        return create_engine(app_flask.config['SQLALCHEMY_DATABASE_URI'], pool_size=20, max_overflow=0)


def query_to_get_iptu_late(engine):
    conn = engine.connect()
    query = text('''SELECT * 
                    FROM iptu as i
                    WHERE status = 'WAITING'
                    OR (status <> 'WAITING' AND DATE_TRUNC('day', updated_at) <= CURRENT_DATE - INTERVAL '1 day');
  ''')
    result = conn.execute(query)
    conn.close()

    return result.fetchall()


def tuple_to_iptu(t):
    return Iptu(
        id=t[0],
        name=t[1],
        code=t[2],
        status=t[3],
        updated_at=t[4],
        inconsistent=t[5]
    )




def schedule_process(app_flask):
    while True:
        trigger_process(app_flask)
        sleep(5)



def trigger_process(app_flask):

    engine = get_engine(app_flask)
    iptu_ids = query_to_get_iptu_late(engine)

    for iptu_id in iptu_ids:
        process_iptu(engine, iptu_id)



    return


from sqlalchemy import text


def process_iptu(engine, iptu):
    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            dono = get_dono_by_iptu(connection, iptu.id)
            cobrancas_to, is_inconsistent, name, address = process_extract_data(iptu, dono if dono != None or dono != [] else '')

            delete_existing_cobrancas(connection, iptu)

            cobrancas = create_cobrancas(cobrancas_to, iptu)

            insert_cobrancas(connection, cobrancas)

            receiver_message = must_send_message_to(connection, iptu.id)
            sended_message = False
            cobrancas_by_iptu = get_all_cobrancas_by_iptu(connection, iptu.id)
            if iptu.send and not is_inconsistent and len(receiver_message) > 0 and cobrancas_by_iptu:
                send_email_and_wpp(iptu, cobrancas, dono)
                sended_message = True

            update_iptu(connection, is_inconsistent, iptu.id, sended_message, name, address)

            transaction.commit()
            connection.close()

        except Exception as e:
            transaction.rollback()
            connection.close()
            print(e)
            raise e


def delete_existing_cobrancas(connection, iptu):
    query = text(
        f"DELETE FROM cobranca as c WHERE c.iptu_id = {iptu.id};"
    )
    connection.execute(query)

def update_iptu(connection, is_inconsistent, iptu_id, sended_message = False, name = None, address = None):
    query = text(
        f'''UPDATE iptu SET status = '{'ERROR' if name == None or name == '' else 'DONE'}', 
                inconsistent = {is_inconsistent},
                updated_at = now() {", last_message = now()" if sended_message else ""},
                address = '{address if address else 'NULL'}',
                name = '{name if name else 'NULL'}'
                WHERE id = {iptu_id};''')
    connection.execute(query)

def must_send_message_to(connection, iptu_id):
    query = text(
        f'''select * from iptu i where i.id = {iptu_id} and 
	( (i.last_message is null) or (extract(month from i.last_message) <> extract(month from now())));'''
    )
    result = connection.execute(query)
    return result.fetchall()


def get_all_cobrancas_by_iptu(connection, iptu_id):
    query = text(
        f'''select * from cobranca c where c.iptu_id = {iptu_id};'''
    )
    result = connection.execute(query)
    return result.fetchall()


def get_dono_by_iptu(connection, iptu_id):
    query = text(
        f'''select * from dono d where d.iptu_id = {iptu_id};'''
    )
    result = connection.execute(query)
    return result.fetchone()


def send_email_and_wpp(iptu, cobrancas, dono):
    body = {
        "phone": dono.numero,
        "email": dono.email,
        "pdf": cobrancas
    }

    requests.post(API_MSG, json=body)

def send_email_and_wpp_model(iptu, cobrancas, dono):
    send_only_email(iptu, cobrancas, dono)
    send_only_wpp(iptu, cobrancas, dono)

def send_only_email(iptu, cobrancas, dono):
    body = {
        "phone": dono.numero,
        "email": dono.email,
        "pdf": [f"""
                    <li>{cobranca.cota}: {cobranca.ano} - R$ {cobranca.total} | <a href="{cobranca.pdf}">Link para acessar o boleto</a></li>
                """ for cobranca in cobrancas]
    }

    requests.post(API_MSG+"/email", json=body)

def send_only_wpp(iptu, cobrancas, dono):
    body = {
        "phone": dono.numero,
        "pdf": [f'{cobranca.cota}: {cobranca.ano} - R$ {cobranca.total}  |  Link para acessar o boleto: {cobranca.pdf}' for cobranca in cobrancas]
    }

    requests.post(API_MSG+"/wpp", json=body)
