from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from rpa_helper import check_exists_by_xpath

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

    #login no site
    self.driver = webdriver.Chrome(service = service, options = options)
    self.driver.get(self.url)
     
  def put_info_web(self, code):
    #input das infos no site (inscrição e o dropwdown)
    verification_label = check_exists_by_xpath('//*[@id="mat-input-0"]', self.driver)
    if verification_label:
      xpath_code_label = '//*[@id="mat-input-0"]'
      code_input = self.driver.find_element(By.XPATH, xpath_code_label)
        
      code_input.send_keys(code)

  def click_on_buttom(self):
      # clickar no botão "Consultar"
      verification_buttom_label = check_exists_by_xpath('//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-footer/button', self.driver)
      if verification_buttom_label:
          buttom_consultar = self.driver.find_element(By.XPATH, '//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-footer/button')

          buttom_consultar.click()
      

robot = Automation()
robot.InitBrowser()
robot.put_info_web('51502046')
