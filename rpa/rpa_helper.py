from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

def check_exists_by_xpath(xpath, driver):
  try:
      driver.find_element(By.XPATH,xpath)
  except NoSuchElementException:
      return False
  return True
