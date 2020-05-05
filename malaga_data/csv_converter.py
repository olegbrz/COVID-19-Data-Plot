import pandas as pd
from numpy import flip
from requests import get
from selenium import webdriver
import logging

# Logger settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s: %(message)s')
file_handler = logging.FileHandler('log_file.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

# Get new link as the old ones expire after some time
def get_new_link():
    logger.info('Initializing WebDriver to get new link to JA data')
    URL = 'https://www.juntadeandalucia.es/institutodeestadisticaycartografia/badea/operaciones/consulta/anual/38228?CodOper=b3_2314&codConsulta=38228'
    chrome_options = webdriver.chrome.options.Options()  
    chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(options=chrome_options)
    logger.info('WebDriver started successfully')
    driver.get(URL)
    logger.info('WebDriver got to the URL')
    driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
    driver.find_element_by_xpath('/html/body/form/div/table/tbody/tr/td[3]/table/tbody/tr/td[4]/a/img').click()
    link = driver.find_element_by_xpath('//*[@id="exportTXT"]').get_attribute('href')
    logger.info('New link obtained')
    driver.quit()
    return link

# Get the data from Consejería de Salud de Andalucía
def update_data():
    logger.info('Getting data from www.juntadeandalucia.es.')
    with open('data/extracted_data.csv', 'wb+') as csv:
        URL = get_new_link()
        r = get(URL)
        csv.write(r.content)
        logger.info('Information written successfully.')

def generate_csv():
    logger.info('Preparing data for plotting.')
    # Columns from csv that we will use
    cols_to_use = [
        'Fecha', 'Territorio',
        'Medida', 'Valor']

    # Import csv
    df = pd.read_csv('data/extracted_data.csv', delimiter=';', usecols=cols_to_use)
    df = df.fillna(0)

    # Set data type of 'Value' as 'int'
    df['Valor'] = df['Valor'].astype('int')

    df_malaga = pd.DataFrame()
    column_dict = {}

    # Get date list and append to dict
    dates = flip(pd.unique(df.query('Territorio == "Málaga"')['Fecha']))
    column_dict = {'Fecha': dates}

    # Measures we are searching for
    measures = ['Confirmados', 'Hospitalizados', 'Total UCI',
                'Fallecimientos', 'Curados']

    for measure in measures:
        measure_isolated = df.query(f'Territorio == "Málaga" and Medida == "{measure}"')
        measure_isolated = measure_isolated.iloc[::-1]      # Reverse values list
        measure_values = measure_isolated['Valor'].values   # Get values
        column_dict.update({measure: measure_values})       # Append to dict

    # Create DataFrame object with rearranged data
    df_malaga = df_malaga.append(pd.DataFrame(column_dict), ignore_index=True)

    # Rename column labels to match datadista labels
    df_malaga = df_malaga.rename(
        columns={
            'Fecha': 'fecha',
            'Confirmados': 'casos',
            'Hospitalizados': 'hospitalizados',
            'Total UCI': 'ingresos_uci',
            'Fallecimientos': 'fallecimientos',
            'Curados': 'altas'})

    # Rearrange columns
    df_malaga = df_malaga[
        ['fecha', 'casos', 'altas', 'fallecimientos',
        'ingresos_uci', 'hospitalizados']]

    # Save to csv
    df_malaga.to_csv('data/norm_data.csv', index=False)
    logger.info('.csv written with success.')