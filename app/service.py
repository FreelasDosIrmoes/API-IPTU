from app import *
from datetime import datetime
from flask import request

from app.model.model import Iptu
from utils.log import Log
from rpa.rpa import Automation


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

def validate_fields(data: dict):
    if 'code' not in data:
        return False, "Campo 'code' não informado"
    if 'owner' not in data:
        return False, "Campo 'owner' não informado"
    if 'email' not in data['owner']:
        return False, "Campo 'email' não informado"
    if 'number' not in data['owner']:
        return False, "Campo 'number' não informado"
    return True, None
