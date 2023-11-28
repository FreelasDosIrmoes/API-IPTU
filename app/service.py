from app import *
from datetime import datetime
from flask import request

from app.model.model import IptuTemp, Iptu
from utils.log import Log
from rpa.rpa import Automation


def process_extract_data(iptu: IptuTemp):
    start_process = datetime.now()
    robot = Automation()
    # previous = robot.process_flux_previous_years(iptu.code, '')
    current = robot.process_flux_current_year(iptu.code, '')
    finish_process = datetime.now()
    Log(request.url).time_all_process(finish_process - start_process)
    # return previous + current
    return current


def create_cobranca(data: list[dict], iptu: Iptu):
    return [dict_to_cobranca(d, iptu) for d in data]


def dict_to_cobranca(d: dict, iptu: Iptu):
    ano = int(d['ano'])
    multa = float(remove_common(d['multa']))
    outros = float(remove_common(d['outros']))
    total = float(remove_common(d['total']))
    cota = d['cota']
    return Cobranca(ano=ano, multa=multa, outros=outros, total=total, cota=cota, iptu=iptu)


def remove_common(var: str):
    return var.replace(",", ".")
