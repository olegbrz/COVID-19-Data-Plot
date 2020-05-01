import pandas as pd
from numpy import flip
from requests import get
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

# Get the data from Consejería de Salud de Andalucía
def update_data():
    logger.info('Getting data from www.juntadeandalucia.es.')
    with open('data/extracted_data.csv', 'wb+') as csv:
        URL ='https://www.juntadeandalucia.es/institutodeestadisticaycartografia/badea/stpivot/stpivot/Print?cube=f7848d22-8912-4b4c-acd2-27dc8daf53a6&type=3&foto=si&ejecutaDesde=&codConsulta=39360&consTipoVisua=JP'
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