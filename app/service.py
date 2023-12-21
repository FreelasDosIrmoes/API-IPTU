from datetime import datetime
from flask import request
from sqlalchemy.engine import Engine
from app.model.model import Iptu, Cobranca, Dono
from app import db, API_MSG
from utils.log import Log
from rpa.rpa import Automation
from sqlalchemy import create_engine, text
from time import sleep
import requests
import base64

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
    # with open('mock.txt', 'r') as f:
    #     data = f.read()
    #     return eval(data), False


def create_cobrancas(data, iptu):
    list = []
    for d in data:
        cobranca = dict_to_cobranca(d, iptu)
        list.append(cobranca)
    return list


def dict_to_cobranca(cobranca_dict, iptu):
    ano = int(cobranca_dict['ano'])
    multa = float(remove_common(cobranca_dict['multa']))
    outros = float(remove_common(cobranca_dict['outros']))
    total = float(remove_common(cobranca_dict['total']))
    cota = cobranca_dict['cota']
    pdf_data = cobranca_dict['pdf_byte']
    return (ano, cota, multa, outros, total, iptu, pdf_data)


def remove_common(var):
    return var.replace(",", ".")


def insert_cobrancas(connection, cobrancas):
    for cobranca in cobrancas:
        query = text(
            '''INSERT INTO cobranca (ano, cota, multa, outros, total, iptu_id, pdf, updated_at)
            VALUES (
                :ano,
                :cota,
                :multa,
                :outros,
                :total,
                :iptu_id,
                :pdf,
                now()
                )'''
        )
        connection.execute(query, {"ano": cobranca[0], "cota": cobranca[1], "multa": cobranca[2], "outros": cobranca[3],
                                   "total": cobranca[4], "iptu_id": cobranca[5].id, "pdf": cobranca[6]})


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
        return create_engine(app_flask.config['SQLALCHEMY_DATABASE_URI'])


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
            if not is_inconsistent and len(receiver_message) > 0 and cobrancas_by_iptu:
                send_email_and_wpp(iptu, cobrancas, dono)
                sended_message = True

            update_iptu(connection, is_inconsistent, iptu.id, sended_message, name, address)

            transaction.commit()
            connection.close()

        except Exception as e:
            transaction.rollback()
            connection.close()
            Log().error_msg(e)
            raise e


def delete_existing_cobrancas(connection, iptu):
    query = text(
        f"DELETE FROM cobranca as c WHERE c.iptu_id = {iptu.id};"
    )
    connection.execute(query)

def update_iptu(connection, is_inconsistent, iptu_id, sended_message = False, name = None, address = None):
    query = text(
        f'''UPDATE iptu SET status = 'DONE', 
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
        "pdf": [base64.b64encode(cobranca[6]).decode('utf-8') for cobranca in cobrancas]
    }

    response = requests.post(API_MSG, json=body)

    if response.status_code == 200:
        Log().info_msg(f"Mensagem enviada para o {dono.nome} com sucesso. IPTU: {iptu.code}")
    else:
        Log().error_msg(f"Erro ao enviar mensagem para o {dono.nome}. IPTU: {iptu.code}. Erro: {response.text}")

def send_email_and_wpp_model(iptu, cobrancas, dono):
    print("send_email_and_wpp_model")
    print([cobranca.pdf is None for cobranca in cobrancas])
    body = {
        "phone": dono.numero,
        "email": dono.email,
        "pdf": [base64.b64encode(cobranca.pdf).decode('utf-8') for cobranca in cobrancas]
    }

    print(body['email'], body['phone'])
    response = requests.post(API_MSG, json=body)

    if response.status_code == 200:
        Log().info_msg(f"Mensagem enviada para o {dono.nome} com sucesso. IPTU: {iptu.code}")
    else:
        Log().error_msg(f"Erro ao enviar mensagem para o {dono.nome}. IPTU: {iptu.code}. Erro: {response.text}")


def send_only_email(iptu, cobranca, dono):
    body = {
        "email": dono.email,
        "pdf": base64.b64encode(cobranca.pdf).decode('utf-8')
    }

    response = requests.post(API_MSG+"/email", json=body)

    if response.status_code == 200:
        Log().info_msg(f"Mensagem enviada para o {dono.nome} com sucesso. IPTU: {iptu.code}")
    else:
        Log().error_msg(f"Erro ao enviar mensagem para o {dono.nome}. IPTU: {iptu.code}. Erro: {response.text}")


def send_only_wpp(iptu, cobranca, dono):
    body = {
        "phone": dono.numero,
        "pdf": base64.b64encode(cobranca.pdf).decode('utf-8')
    }

    response = requests.post(API_MSG+"/wpp", json=body)

    if response.status_code == 200:
        Log().info_msg(f"Mensagem enviada para o {dono.nome} com sucesso. IPTU: {iptu.code}")
    else:
        Log().error_msg(f"Erro ao enviar mensagem para o {dono.nome}. IPTU: {iptu.code}. Erro: {response.text}")