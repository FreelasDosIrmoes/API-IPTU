import os

from datetime import datetime
from dotenv import load_dotenv
from time import sleep

from anticaptchaofficial.recaptchav2enterpriseproxyless import *

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from rpa.rpa_helper import *
from rpa.variables import *

from math import ceil
from utils.log import Log


class Automation:
  def __init__(self, route = '/api/iptu'):
    self.url = url_site

    self.service = Service()
    self.options = webdriver.ChromeOptions()
    self.options.add_argument("--headless=new")
    self.options.add_argument('--no-sandbox')
    self.options.add_argument('--disable-dev-shm-usage')
    self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
    self.options.add_argument('--log-level=3')
    self.options.add_argument('--disable-blink-features=AutomationControlled')
    self.options.add_experimental_option("prefs", {
      "download.default_directory": PATH_DOWNLOAD,
      "download.prompt_for_download": False,
      "download.directory_upgrade": False,
      "safebrowsing.enabled": True
    })
    
    self.route = route

  def process_flux_current_year(self, code, owner):
    # fluxo do processo de automação do ano atual
    self.init_browser()
    self.put_info_web(code)
    self.passed_on_captcha()
    if self.click_on_buttom():
      return self.extract_data_web(owner)
    return None, False
  
  def process_flux_previous_years(self, code, owner):
  # fluxo do processo de automação dos anos anteriores
    self.init_browser()
    self.put_info_web_last_years(code)
    self.passed_on_captcha()
    if self.click_on_buttom():
      return self.extract_data_web(owner)
    return None, False, None, None

  def init_browser(self):
    #login no site
    self.driver = webdriver.Chrome(service = self.service, options = self.options)
    self.driver.get(self.url)

  def put_info_web(self, code):
    #input das infos no site (inscrição e o dropwdown)
    if check_exists_by_xpath(xpath_code_label, self.driver):
      code_input = self.driver.find_element(By.XPATH, xpath_code_label)

      code_input.clear()
      code_input.send_keys(code)

  def click_on_buttom(self):
    # clickar no botão "Consultar"
    if check_exists_by_xpath(xpath_buttom_submit, self.driver):
      buttom_consultar = self.driver.find_element(By.XPATH, xpath_buttom_submit)
      buttom_consultar.click()
      sleep(1.5)  # ver se tira (desperdício)
      return not check_exists_by_xpath(xpath_error_msg, self.driver)
    return False

  def passed_on_captcha(self):
    # passar do recaptch
    start_captcha = datetime.now()
    solver = recaptchaV2EnterpriseProxyless()
    solver.set_verbose(1)
    solver.set_key(API_KEY)
    solver.set_website_url(url_site)
    solver.set_website_key(WEB_KEY)

    g_response = solver.solve_and_return_solution()
    if g_response != 0:

      # preencher o campo que do captcha para a liberação
      # g-recaptcha-response

      self.driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "{}";'.format(g_response))
      self.driver.execute_script(f"___grecaptcha_cfg.clients[0].A.A.callback('{g_response}')")
      final_captcha = datetime.now()
      
      Log(self.route).time_captcha(final_captcha-start_captcha)
    else:
      Log(self.route).error_msg(solver.error_code)

  def extract_data_web(self, owner):
    # extrair os dados do site 
    sleep(2)
    flg_inconsistente = False
    
    if check_exists_by_xpath(expand_table, self.driver):
      label_click = self.driver.find_element(By.XPATH, expand_table)
      label_click.click()  

    if (owner != '' and owner is not None) and not verify_owner(owner, xpath_label_name, self.driver):
      flg_inconsistente = True

    if check_exists_by_xpath(xpath_label_endereco, self.driver):
      label_endereco = self.driver.find_element(By.XPATH, xpath_label_endereco)
      endereco = label_endereco.text
    
    if check_exists_by_xpath(xpath_label_name, self.driver):
        label_name = self.driver.find_element(By.XPATH, xpath_label_name)
        name = label_name.text
    
    row = 1
    column = 1

    table_data = []
      
    qtd_page = self.returning_qtd_page()

    if qtd_page is None:
      return [], False, None, None
    
    if qtd_page <= 10:
      # caso com menos ou igual a 10 débitos na página
      get_data_table(self.driver, table_data, row, column)
        
      return table_data, flg_inconsistente, name, endereco
    else:
      # caso com mais de 10 débitos na página
      num = ceil(qtd_page / 10)
      
      for i in range(num):
        get_data_table(self.driver, table_data, row, column)
        
        click_next_page(self.driver)
        
      return table_data, flg_inconsistente, name, endereco
  
  def put_info_web_last_years(self, code):    # TODO BOTAR O OWNER AQUI TB
    # input das infos no site (inscrição e o dropwdown)
    if check_exists_by_xpath(xpath_code_label, self.driver):
      code_input = self.driver.find_element(By.XPATH, xpath_code_label)

      code_input.clear()
      code_input.send_keys(code)
    if check_exists_by_xpath(expand_last_years, self.driver):
      dropdown_year = self.driver.find_element(By.XPATH, expand_last_years)
      dropdown_year.click()
      if check_exists_by_xpath(xpath_label_last_years, self.driver):
        label_last_yers = self.driver.find_element(By.XPATH, xpath_label_last_years)
        label_last_yers.click()
        
  def returning_qtd_page(self):
    # retornar número de débitos
    if check_exists_by_xpath(xpath_qtd_page, self.driver):
      label = self.driver.find_element(By.XPATH, xpath_qtd_page).text.strip()
      qtd_page = int(label[-1])
      
      return qtd_page
  