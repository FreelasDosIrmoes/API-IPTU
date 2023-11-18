from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from rpa_helper import check_exists_by_xpath
from time import sleep

from anticaptchaofficial.recaptchav2enterpriseproxyless import *

class Automation:
  def __init__(self):
    self.url = "https://ww1.receita.fazenda.df.gov.br/emissao-segunda-via/iptu" 
  
  def InitBrowser(self):     
    #configs
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)   # tirar dps
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--log-level=3')
    options.add_argument('--disable-blink-features=AutomationControlled')

    #login no site
    self.driver = webdriver.Chrome(service = service, options = options)
    self.driver.get(self.url)
     
  def put_info_web(self, code):
    #input das infos no site (inscrição e o dropwdown)
    verification_label = check_exists_by_xpath('//*[@id="mat-input-0"]', self.driver)
    if verification_label:
      xpath_code_label = '//*[@id="mat-input-0"]'
      code_input = self.driver.find_element(By.XPATH, xpath_code_label)
      
      code_input.clear()
      code_input.send_keys(code)

  def click_on_buttom(self):
      # clickar no botão "Consultar"
      verification_buttom_label = check_exists_by_xpath('//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-footer/button', self.driver)
      if verification_buttom_label:
          buttom_consultar = self.driver.find_element(By.XPATH, '//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-footer/button')

          buttom_consultar.click()
  
  def passed_on_captcha(self):
  
    solver = recaptchaV2EnterpriseProxyless()
    solver.set_verbose(1)
    solver.set_key("3f6496391630e35dff64c09607c4b729")
    solver.set_website_url("https://ww1.receita.fazenda.df.gov.br/emissao-segunda-via/iptu")
    solver.set_website_key("6LcppFcmAAAAANtBOCHWWX9Z34UrWtunr7GsqQyt")

    g_response = solver.solve_and_return_solution()
    if g_response != 0:
       
        # preencher o campo que do captcha para a liberação
        # g-recaptcha-response 

        self.driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "{}";'.format(g_response))
        self.driver.execute_script(f"___grecaptcha_cfg.clients[0].M.M.callback('{g_response}')")
    else:
        print ("task finished with error "+ solver.error_code)

  def extract_data(self):
    pass

robot = Automation()
robot.InitBrowser()
robot.put_info_web('51502046')
robot.passed_on_captcha()
robot.click_on_buttom()
robot.extract_data()