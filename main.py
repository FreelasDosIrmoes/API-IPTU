from rpa.rpa import Automation
from utils.log import Log
from datetime import datetime

start_process = datetime.now()
try:
  robot = Automation()
  robot.process_flux_current_year('48517852', 'BRAZILIAN SECURITIES COMPANHIA DE SECURITIZACAO')
  finish_process = datetime.now()
  Log().time_all_process(finish_process-start_process)
except Exception as e:
  Log().error_msg(e)