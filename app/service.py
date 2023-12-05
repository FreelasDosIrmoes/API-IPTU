from datetime import datetime
from flask import request
from app import app
from app.model.model import Iptu, Cobranca
from utils.log import Log
from rpa.rpa import Automation
from sqlalchemy import create_engine, text
from sqlalchemy.orm import registry


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


def query_to_get_iptu_late(app_flask):
    with app_flask.app_context():
        engine = create_engine(app_flask.config['SQLALCHEMY_DATABASE_URI'], echo=True)
        conn = engine.connect()
        query = text('''SELECT *
                        FROM iptu
                        WHERE status = 'WAITING'
                           OR (status = 'DONE' AND
                               EXTRACT(DAY FROM AGE(CURRENT_DATE, updated_at AT TIME ZONE 'UTC' AT TIME ZONE '-03:00')) >= 1);
      ''')
        result = conn.execute(query)

        return [tuple_to_iptu(t) for t in result.fetchall()]


def tuple_to_iptu(t):
    return Iptu(
        id=t[0],
        name=t[1],
        code=t[2],
        address=t[3],
        status=t[4],
        updated_at=t[5]
    )


def get_cobrancas_payed(cobrancas: list[Cobranca], cobrancas_db: list[Cobranca]):
    cobrancas_payed = []
    for cobranca_no_banco in cobrancas_db:
        presente = False
        for recebida in cobrancas:
            if cobranca_no_banco == recebida:
                presente = True
                break
        if not presente:
            cobrancas_payed.append(cobranca_no_banco)
    return cobrancas_payed
