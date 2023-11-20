import os

from dotenv import load_dotenv
from time import sleep

from anticaptchaofficial.recaptchav2enterpriseproxyless import *

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from rpa.rpa_helper import *
from rpa.variables import *

load_dotenv()

API_KEY = os.getenv('API_KEY')
WEB_KEY = os.getenv('WEB_KEY')


class Automation:
  def __init__(self):
    self.url = url_site

    self.service = Service()
    self.options = webdriver.ChromeOptions()
    self.options.add_experimental_option("detach", True)   # tirar dps
    self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
    self.options.add_argument('--log-level=3')
    self.options.add_argument('--disable-blink-features=AutomationControlled')

  def process_flux(self, code, owner):
    # fluxo do processo de automação
    self.init_browser()
    self.put_info_web(code)
    self.passed_on_captcha()
    self.click_on_buttom()
    self.extract_data_web(owner)

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

  def passed_on_captcha(self):
    # passar do recaptch
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
        self.driver.execute_script(f"___grecaptcha_cfg.clients[0].M.M.callback('{g_response}')")
    else:
        print ("task finished with error "+ solver.error_code)

  def extract_data_web(self, owner):
    # extrair os dados do site 
    sleep(2)
    
    if check_exists_by_xpath(expand_table, self.driver):
      label_click = self.driver.find_element(By.XPATH, expand_table)
      label_click.click()  

    if not verify_owner(owner, xpath_label_name, self.driver):
      return

    if check_exists_by_xpath(xpath_label_endereco, self.driver):
      label_endereco = self.driver.find_element(By.XPATH, xpath_label_endereco)
   
    row = 1
    column = 1

    table_data = []
    
    while check_exists_by_xpath(get_xpath(row, column), self.driver):
      dict = {}

      while check_exists_by_xpath(get_xpath(row, column), self.driver):
        cell_xpath = get_xpath(row, column)
        label_column = self.driver.find_element(By.XPATH, cell_xpath).text
        
        if ('Imprimir') in label_column:
          break
        
        build_dict(dict,column, label_column)

        column += 1

      table_data.append(dict)
      column = 1
      row += 1

    print(table_data)
