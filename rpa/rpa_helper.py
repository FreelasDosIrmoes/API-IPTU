from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

def check_exists_by_xpath(xpath, driver):
  try:
      driver.find_element(By.XPATH,xpath)
  except NoSuchElementException:
      return False
  return True

def get_xpath(count, cell_number):
    return (f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card'
            f'/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{count}]/m'
            f'at-cell[{cell_number}]')

def verify_owner(owner, xpath_owner, driver):
    if check_exists_by_xpath(xpath_owner, driver):
      name = driver.find_element(By.XPATH, xpath_owner).text
      
      if owner == name:
        return True
    return False
          