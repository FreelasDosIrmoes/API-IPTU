from app import *
from datetime import datetime
from flask import request

from app.model.model import IptuTemp
from utils.log import Log
from rpa.rpa import Automation


def process_extract_data(iptu: IptuTemp):
    start_process = datetime.now()
    robot = Automation()
    # previous = robot.process_flux_previous_years(iptu.code, '')
    current = robot.process_flux_current_year(iptu.code, '')
    finish_process = datetime.now()
    Log(request.url).time_all_process(finish_process - start_process)
    return [] + current


def create_cobranca(data: list[dict]):
    cobrancas = []
    for i in data:
        cobranca = Cobranca(
            ano=i['ano'], cota=i['cota'], valor=i['valor'], multa=i['multa'], juros=i['juros'], outros=i['outros'],
            total=i['total']
        )
        cobrancas.append(cobranca)
    return cobrancas
