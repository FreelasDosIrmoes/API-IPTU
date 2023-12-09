import logging

class Log:
  def __init__(self, route=''):
    self.route = route
    
    logging.basicConfig(level=logging.INFO, filename="logger.log", format="%(asctime)s - %(levelname)s - %(message)s")
  
  def time_captcha(self, time):
    logging.info(f"{self.route} - Tempo do Captcha {time}")

  def time_all_process(self, time):
    logging.info(f"{self.route} - Tempo total da Automacao {time}")
  
  def error_msg(self, error):
    logging.error(f"{self.route} - Error encontrado: {error}")

  def info_msg(self, msg):
    logging.info(f"{self.route} - {msg}")