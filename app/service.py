from datetime import datetime
from flask import request
from app import app
from app.model.model import Iptu, Cobranca
from utils.log import Log
from rpa.rpa import Automation
from sqlalchemy import create_engine, text
from sqlalchemy.orm import registry



def process_extract_data(iptu: Iptu):
    # start_process = datetime.now()
    # robot = Automation()
    # previous = robot.process_flux_previous_years(iptu.code, '')
    # current = robot.process_flux_current_year(iptu.code, '')
    # finish_process = datetime.now()
    # Log(request.url).time_all_process(finish_process - start_process)
    # previous = previous if previous else []
    # current = current if current else []
    return [
	{
		"id" : 55,
		"ano" : '2022',
		"cota" : "CDA 50227891783 IPTU",
		"multa" : '51.67',
		"outros" : '67.61',
		"total" : '743.71',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 56,
		"ano" : '2022',
		"cota" : "CDA 50229734570 TLP",
		"multa" : '21.62',
		"outros" : '28.29',
		"total" : '311.25',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 57,
		"ano" : '2021',
		"cota" : "CDA 50217633781 IPTU",
		"multa" : '46.79',
		"outros" : '65.17',
		"total" : '716.95',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 58,
		"ano" : '2021',
		"cota" : "CDA 50219135207 TLP",
		"multa" : '19.49',
		"outros" : '27.14',
		"total" : '298.6',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 59,
		"ano" : '2020',
		"cota" : "CDA 50211684236 IPTU",
		"multa" : '45.45',
		"outros" : '64.39',
		"total" : '708.29',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 60,
		"ano" : '2020',
		"cota" : "CDA 50213253801 TLP",
		"multa" : '18.52',
		"outros" : '26.24',
		"total" : '288.65',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 61,
		"ano" : '2023',
		"cota" : "01 IPTU\/TLP",
		"multa" : '12.95',
		"outros" : '0.0',
		"total" : '151.3',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 62,
		"ano" : '2023',
		"cota" : "02 IPTU\/TLP",
		"multa" : '12.95',
		"outros" : '0.0',
		"total" : '149.78',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 63,
		"ano" : '2023',
		"cota" : "03 IPTU\/TLP",
		"multa" : '12.95',
		"outros" : '0.0',
		"total" : '148.25',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 64,
		"ano" : "2023",
		"cota" : "04 IPTU\/TLP",
		"multa" : '12.95',
		"outros" : '0.0',
		"total" : '146.63',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	},
	{
		"id" : 65,
		"ano" : '2023',
		"cota" : "05 IPTU\/TLP",
		"multa" : '12.95',
		"outros" : '0.0',
		"total" : '145.25',
		"iptu_id" : 1,
		"pdf" : None,
		"updated_at" : "2023-11-30T22:55:08.621Z"
	}
]


def create_cobranca(data: list[dict], iptu: Iptu):
    return [dict_to_cobranca(d, iptu) for d in data]


def dict_to_cobranca(cobranca_dict: dict, iptu: Iptu):
    ano = int(cobranca_dict['ano'])
    multa = float(remove_common(cobranca_dict['multa']))
    outros = float(remove_common(cobranca_dict['outros']))
    total = float(remove_common(cobranca_dict['total']))
    cota = cobranca_dict['cota']
    pdf_data = cobranca_dict['pdf']
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
    for cobranca_db in cobrancas_db:
        if cobranca_db not in cobrancas:
            cobrancas_payed.append(cobranca_db)
        else:
            cobranca_db.updated_at = datetime.now()
    return cobrancas_payed
