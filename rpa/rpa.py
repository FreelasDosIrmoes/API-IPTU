from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from rpa_helper import check_exists_by_xpath

class Automation:
  def InitBrowser(self):
    #configs
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)   # tirar dps
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--log-level=3')

    #login no site
    url = "https://ww1.receita.fazenda.df.gov.br/emissao-segunda-via/iptu"

    self.driver = webdriver.Chrome(service = service, options = options)
    self.driver.get(url)
     
  def put_info_web(self):
    #input das infos no site (inscrição e o dropwdown)
    xpath_code_label = '//*[@id="mat-input-0"]'
    code_input = self.driver.find_element(By.XPATH, xpath_code_label)
      
    code_input.send_keys('51502046')
    
        

robot = Automation()
robot.InitBrowser()
robot.put_info_web()