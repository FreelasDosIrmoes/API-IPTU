import os

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from rpa.variables import *
from time import sleep
from datetime import datetime


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

      return str(owner).upper() == str(name).upper()

def build_dict(dict, col, data):
    ano_atual = str(datetime.now().year)
    
    data_atual = datetime.now()

    if col == 1:
        dict['ano'] = data
    elif col == 2:
        dict['cota'] = data
        
        if dict['ano'] != ano_atual:
            dict['a_vencer'] = False
        else:
            
            if tem_numero(data):
                
                if '01' in data:
                    data_cobranca = f'01/05/{ano_atual}'
                elif '02' in data:
                    data_cobranca = f'01/06/{ano_atual}'
                elif '03' in data:
                    data_cobranca = f'01/07/{ano_atual}'
                elif '04' in data:
                    data_cobranca = f'01/08/{ano_atual}'
                elif '05' in data:
                    data_cobranca = f'01/09/{ano_atual}'
                elif '06' in data:
                    data_cobranca = f'01/10/{ano_atual}'
                    
                data_cobranca = datetime.strptime(data_cobranca, '%d/%m/%Y')
                if data_cobranca <= data_atual:
                    dict['a_vencer'] = False
                elif data_cobranca > data_atual:
                    dict['a_vencer'] = True
                else:
                    dict['a_vencer'] = False
        
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


def process_pdf(data, driver, row):
    remove_all_relatorio_dar()
    button_download_pdf = get_xpath_button_download(row)
    if check_exists_by_xpath(button_download_pdf, driver):
        sleep(1.5)        
        driver.find_element(By.XPATH, button_download_pdf).click()
        sleep(0.5)
        if check_exists_by_xpath(xpath_click_continue_pdf_dowloads, driver):
            driver.find_element(By.XPATH, xpath_click_continue_pdf_dowloads).click()
        if check_exists_by_xpath(button_confirmation_pdf, driver):
            driver.find_element(By.XPATH, button_confirmation_pdf).click()
        verify_download()
        with open(PATH_DOWNLOAD + "RelatorioDAR.pdf", "rb") as file:
            data['pdf_byte'] = file.read()
        os.remove(PATH_DOWNLOAD + "RelatorioDAR.pdf")


def remove_all_relatorio_dar():
    for file in os.listdir(PATH_DOWNLOAD):
        if "RelatorioDAR" in file:
            os.remove(PATH_DOWNLOAD+file)


def get_xpath_button_download(row):
    return f'//mat-table/mat-row[{row}]/mat-cell[8]/button/span[contains(text(), " Gerar PDF ")]'

def verify_download():
    while True:
        path_complete = os.path.join(PATH_DOWNLOAD, "RelatorioDAR.pdf")

        if os.path.isfile(path_complete):
            sleep(0.5)
            return

def verify_data(table_data):
    for data in table_data:
        if "pdf_byte" not in data.keys():
            raise Exception("o dicionário", data, "não possui o campo 'pdf_byte'.")
        if data['pdf_byte'] == b'':
            raise Exception("o dicionário", data, "possui o campo 'pdf_byte' vazio.")

def get_data_table(driver, table_data, row, column):  
    while check_exists_by_xpath(get_xpath_table(row, column), driver):
        dict = {}
        
        while check_exists_by_xpath(get_xpath_table(row, column), driver):
          sleep(0.5)
          cell_xpath = get_xpath_table(row, column)
          label_column = driver.find_element(By.XPATH, cell_xpath).text
          
          if ('Gerar PDF') in label_column:
            process_pdf(dict, driver, row)
            break
          
          build_dict(dict,column, label_column)

          column += 1

        table_data.append(dict)
        column = 1
        row += 1
        
def click_next_page(driver):
    if check_exists_by_xpath(xpath_next_page, driver):
      label_next_page = driver.find_element(By.XPATH, xpath_next_page)
      label_next_page.click()
      

def tem_numero(string):
    for caractere in string:
        if caractere.isdigit():
            return True
    return False