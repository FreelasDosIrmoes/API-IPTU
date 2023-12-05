from datetime import datetime
from flask import request

from app.model.model import Iptu, Cobranca, Dono
from utils.log import Log
from rpa.rpa import Automation
from sqlalchemy import create_engine, text


def process_extract_data(iptu: Iptu):
    start_process = datetime.now()
    robot = Automation()
    previous = robot.process_flux_previous_years(iptu.code, '')
    current = robot.process_flux_current_year(iptu.code, '')
    finish_process = datetime.now()
    Log(request.url).time_all_process(finish_process - start_process)
    previous = previous if previous else []
    current = current if current else []
    return previous + current


def create_cobranca(data: list[dict], iptu: Iptu):
    return [dict_to_cobranca(d, iptu) for d in data]


def dict_to_cobranca(cobranca_dict: dict, iptu: Iptu):
    ano = int(cobranca_dict['ano'])
    multa = float(remove_common(cobranca_dict['multa']))
    outros = float(remove_common(cobranca_dict['outros']))
    total = float(remove_common(cobranca_dict['total']))
    cota = cobranca_dict['cota']
    pdf_data = cobranca_dict['pdf_byte']
    return Cobranca(ano=ano, multa=multa, outros=outros,
                    total=total, cota=cota, iptu=iptu,
                    pdf=pdf_data)


def remove_common(var: str):
    return var.replace(",", ".")


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


def query_to_get_iptu_late(app_flask):
    with app_flask.app_context():
        engine = create_engine(app_flask.config['SQLALCHEMY_DATABASE_URI'], echo=True)
        conn = engine.connect()
        query = text('''SELECT i.id 
                        FROM iptu as i
                        WHERE status = 'WAITING'
                        OR (status <> 'WAITING' AND DATE_TRUNC('day', updated_at) = CURRENT_DATE - INTERVAL '1 day');
      ''')
        result = conn.execute(query)

        return [t[0] for t in result.fetchall()]


def tuple_to_iptu(t):
    return Iptu(
        id=t[0],
        name=t[1],
        code=t[2],
        address=t[3],
        status=t[4],
        updated_at=t[5]
    )
