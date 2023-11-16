from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def check_exists_by_xpath(xpath):
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = webdriver.Chrome(options=chrome_options)
  try:
      driver.find_element(By.XPATH,xpath)
  except NoSuchElementException:
      return False
  return True


#TODO VER A QUESTÃO DE RECEBER O DRIVER (OU SOLUÇÃO POO)

