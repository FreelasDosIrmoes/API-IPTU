
def get_xpath(count, cell_number):
      return f'//*[@id="containerPrincipal"]/div/app-emissao-dar-iptu/shared-page/shared-page-content/div/mat-card/mat-card-content/shared-responsive-selector/res-desktop/div/mat-table/mat-row[{count}]/mat-cell[{cell_number}]'
    

print(get_xpath(1, 1))