import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv('API_KEY')
WEB_KEY = os.getenv('WEB_KEY')
PATH_DOWNLOAD = os.getenv('PASTA_DOWNLOAD')

xpath_code_label = '//*[@id="mat-input-0"]'
xpath_buttom_submit = '//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-footer/button'

xpath_label_name = '//*[@id="InfoCabecalho"]/mat-card/mat-card-content/shared-description-list/shared-term[2]/div'
xpath_label_endereco = '//*[@id="InfoCabecalho"]/mat-card/mat-card-content/shared-description-list/shared-term[3]/div'

expand_table = '//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/h6/a'

expand_last_years = '//*[@id="exercicio"]/div/div[2]'
xpath_label_last_years = '//*[@id="mat-option-1"]/span'
xpath_error_msg = '//*[@id="cdk-overlay-2"]/snack-bar-container/simple-snack-bar/span'

xpath_qtd_page = '//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/mat-paginator/div/div/div[2]/div'
xpath_next_page = '//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/mat-paginator/div/div/div[2]/button[2]'

xpath_click_continue_pdf_dowloads = '//div[4]/button'

url_site = 'https://ww1.receita.fazenda.df.gov.br/emissao-segunda-via/iptu'

button_confirmation_pdf = '//button/span[contains(text(), "Confirmar")]'