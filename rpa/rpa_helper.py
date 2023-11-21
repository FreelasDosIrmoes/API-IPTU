import os

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from rpa.variables import button_confirmation_pdf
from time import sleep

def check_exists_by_xpath(xpath, driver):
  try:
      driver.find_element(By.XPATH,xpath)
  except NoSuchElementException:
      return False
  return True

def get_xpath_table(count, cell_number):
    return (f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card'
            f'/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{count}]/m'
            f'at-cell[{cell_number}]')

def verify_owner(owner, xpath_owner, driver):
    if check_exists_by_xpath(xpath_owner, driver):
      name = driver.find_element(By.XPATH, xpath_owner).text

      if owner == name:
        return True
    return False

def build_dict(dict, col, data):
    if col == 1:
        dict['ano'] = data
    elif col == 2:
        dict['cota'] = data
    elif col == 3:
        dict['valor'] = data
    elif col == 4:
        dict['multa'] = data
    elif col == 5:
        dict['juros'] = data
    elif col == 6:
        dict['outros'] = data
    elif col == 7:
      dict['total'] = data



def process_pdf(data, driver, row, column):
    button_download_pdf = get_xpath_table(row, column) + '//button/span[contains(text(), " Gerar PDF ")]'
    if check_exists_by_xpath(button_download_pdf, driver):
        driver.find_element(By.XPATH, button_download_pdf).click()
        if check_exists_by_xpath(button_confirmation_pdf, driver):
            driver.find_element(By.XPATH, button_confirmation_pdf).click()
        sleep(5)
        with open("/home/arthur/Downloads/RelatorioDAR.pdf", "rb") as file:
            data['pdf_byte'] = file.read()
        os.remove("/home/arthur/Downloads/RelatorioDAR.pdf")
