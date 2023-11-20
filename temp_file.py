'VARIABLES.py'

expand_last_years = '//*[@id="exercicio"]/div/div[2]'
xpath_label_last_years = '//*[@id="mat-option-1"]/span'
xpath_error_msg = '//*[@id="cdk-overlay-2"]/snack-bar-container/simple-snack-bar/span'

# TODO VER A QUESTÃO DE PASSAR AS PÁGINAS NOS ANOS ANTERIORES PARA PEGAR TUDO ( TER O IPTU Q TENHA ANOS ANTERIORES)

'rpa.py'

    def put_info_web_last_years(self, code):    # TODO BOTAR O OWNER AQUI TB
        # input das infos no site (inscrição e o dropwdown)
        if check_exists_by_xpath(xpath_code_label, self.driver):
            code_input = self.driver.find_element(By.XPATH, xpath_code_label)

            code_input.clear()
            code_input.send_keys(code)
        if check_exists_by_xpath(expand_last_years, self.driver):
            dropdown_year = self.driver.find_element(By.XPATH, expand_last_years)
            dropdown_year.click()
            if check_exists_by_xpath(xpath_label_last_years, self.driver):
                label_last_yers = self.driver.find_element(By.XPATH, xpath_label_last_years)
                label_last_yers.click()


def process_flux_previous_years(self, code, owner):
  # fluxo do processo de automação dos anos anteriores
        self.init_browser()
        self.put_info_web_last_years(code)
        self.passed_on_captcha()
        if self.click_on_buttom():
            self.extract_data_web(owner)

def process_flux_current_year(self, code, owner):
        # fluxo do processo de automação do ano atual
        self.init_browser()
        self.put_info_web(code)
        self.passed_on_captcha()
        if self.click_on_buttom():
            self.extract_data_web(owner)

def click_on_buttom(self):
        # clickar no botão "Consultar"
        if check_exists_by_xpath(xpath_buttom_submit, self.driver):
            buttom_consultar = self.driver.find_element(By.XPATH, xpath_buttom_submit)
            buttom_consultar.click()
            sleep(1)  # ver se tira (desperdício)
            if check_exists_by_xpath(xpath_error_msg, self.driver):
                return False       # NÃO EXISTE DÉBITOS DE ANOS ANTERIORES
            return True
        return False
        
