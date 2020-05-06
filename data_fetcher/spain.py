import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(levelname)s:%(asctime)s:%(name)s: %(message)s')
file_handler = logging.FileHandler('log_file.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

# Get the data
def update_data():
    url = 'https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/nacional_covid19.csv'

    logger.info('Getting Spain data from datadista GitHub.')
    df_spain = pd.read_csv(url, delimiter=',', parse_dates=['fecha'])
    logger.info('Success.')
    df_spain = df_spain.fillna(0)
    logger.info('Writing Spain data to csv.')
    df_spain.to_csv('data/spain_data.csv', index=False)
    logger.info('Spain data written successfully.')