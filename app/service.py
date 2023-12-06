import multiprocessing
import schedule
from datetime import datetime
from flask import request
from sqlalchemy.engine import Engine
from app.model.model import Iptu, Cobranca, Dono
from app import db
from utils.log import Log
from rpa.rpa import Automation
from sqlalchemy import create_engine, text


def process_extract_data(iptu: Iptu):
    # start_process = datetime.now()
    # robot = Automation()
    # previous, is_inconsistent_previous = robot.process_flux_previous_years(iptu.code, '')
    # current, is_inconsistent_current = robot.process_flux_current_year(iptu.code, '')
    # finish_process = datetime.now()
    # Log().time_all_process(finish_process - start_process)
    # previous = previous if previous else []
    # current = current if current else []
    # return previous + current, is_inconsistent_current or is_inconsistent_previous
    with open('mock.txt', 'r') as f:
        return eval(f.read()), False


def create_cobrancas(data: list[dict], iptu: Iptu):
    list = []
    for d in data:
        cobranca = dict_to_cobranca(d, iptu)
        list.append(cobranca)
    return list


def dict_to_cobranca(cobranca_dict: dict, iptu: Iptu):
    ano = int(cobranca_dict['ano'])
    multa = float(remove_common(cobranca_dict['multa']))
    outros = float(remove_common(cobranca_dict['outros']))
    total = float(remove_common(cobranca_dict['total']))
    cota = cobranca_dict['cota']
    pdf_data = cobranca_dict['pdf_byte']
    return (ano, cota, multa, outros, total, iptu, pdf_data)


def remove_common(var: str):
    return var.replace(",", ".")


def insert_cobrancas(connection, cobrancas: list[tuple]):
    for cobranca in cobrancas:
        query = text(
            '''INSERT INTO cobranca (ano, cota, multa, outros, total, iptu_id, pdf) 
            VALUES (
                :ano,
                :cota,
                :multa,
                :outros,
                :total,
                :iptu_id,
                :pdf
                )'''
        )
        connection.execute(query, {"ano": cobranca[0], "cota": cobranca[1], "multa": cobranca[2], "outros": cobranca[3],
                                   "total": cobranca[4], "iptu_id": cobranca[5].id, "pdf": cobranca[6]})


def validate_fields_post(data: dict):
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


def build_iptu_and_dono(data: dict[str]) -> (Iptu, Dono):
    iptu = Iptu(code=data['code'], name=data['name'], status="WAITING")
    dono = Dono(email=data['owner']['email'], numero=data['owner']['number'], iptu=iptu)
    return iptu, dono


def validate_fields_put(data: dict):
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


def build_request(iptu: Iptu, cobrancas: list[Cobranca]):
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
        'updated_at': iptu.updated_at.astimezone().strftime('%d-%m-%Y %H:%M:%S %Z')
    }


def get_engine(app_flask) -> Engine:
    with app_flask.app_context():
        return create_engine(app_flask.config['SQLALCHEMY_DATABASE_URI'], echo=True)


def query_to_get_iptu_late(engine):
    conn = engine.connect()
    query = text('''SELECT * 
                    FROM iptu as i
                    WHERE status = 'WAITING'
                    OR (status <> 'WAITING' AND DATE_TRUNC('day', updated_at) <= CURRENT_DATE - INTERVAL '1 day');
  ''')
    result = conn.execute(query)

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
    schedule.every(1).minutes.do(trigger_process, app_flask)
    while True:
        schedule.run_pending()


automation_status = multiprocessing.Value("i", 0)


def trigger_process(app_flask):
    if automation_status.value == 1:
        return {"message": "Automação em execução"}, 409

    automation_status.value = 1

    try:
        engine = get_engine(app_flask)
        iptu_ids = query_to_get_iptu_late(engine)

        for iptu_id in iptu_ids:
            process_iptu(engine, iptu_id)

    finally:
        automation_status.value = 0

    return {"message": "Automação finalizada"}, 201


from sqlalchemy import text


def process_iptu(engine, iptu):
    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            cobrancas_to, is_inconsistent = process_extract_data(iptu)

            if not cobrancas_to:
                Log().error_msg(f"AUTOMAÇÃO RETORNOU UMA LISTA VAZIA PARA O CODIGO: {iptu.code}")
                return

            delete_existing_cobrancas(connection, iptu)

            cobrancas = create_cobrancas(cobrancas_to, iptu)
            for c in cobrancas:
                print(c)
                for d in c:
                    print(d, type(d))
            insert_cobrancas(connection, cobrancas)

            update_iptu(connection, is_inconsistent, iptu.id)

            transaction.commit()

        except Exception as e:
            transaction.rollback()
            Log().error_msg(e)
            raise e


def delete_existing_cobrancas(connection, iptu):
    query = text(
        f"DELETE FROM cobranca as c WHERE c.iptu_id = {iptu.id};"
    )
    connection.execute(query)

def update_iptu(connection, is_inconsistent: bool, iptu_id: int):
    query = text(
        f'''UPDATE iptu SET status = 'DONE', 
                updated_at = '{datetime.now()}', 
                inconsistent = {is_inconsistent} 
                WHERE id = {iptu_id};''')
    connection.execute(query)