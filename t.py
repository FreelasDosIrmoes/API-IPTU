import locale

def format_number(value):
    locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

    value = value.replace('.', '')

    formatted_number = locale.atof(value)
    
    return formatted_number



number = '1.710,29'


print(format_number(number))