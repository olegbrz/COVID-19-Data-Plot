import logging
from os.path import getmtime
from time import ctime, time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import data_fetcher.malaga
import data_fetcher.spain 

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

def date_parse_malaga(x): return pd.datetime.strptime(x, '%d/%m/%Y')
def date_parse_spain(x): return pd.datetime.strptime(x, '%Y-%m-%d')

# Actualiza si el CSV tiene más de 30 mins de antiguedad
try:
    if time() - getmtime('data/malaga_data.csv') > (30 * 60):
        logger.info('Updating malaga_data.csv...')
        data_fetcher.malaga.update_data()
    else:
        logger.info("File malaga_data.csv is recent, won't be updated.")
except:
    logger.info('File malaga_data.csv not found, downloading...')
    data_fetcher.malaga.update_data()

try:
    if time() - getmtime('data/spain_data.csv') > (30 * 60):
        logger.info('Updating spain_data.csv...')
        data_fetcher.spain.update_data()
    else:
        logger.info("File spain_data.csv is recent, won't be updated.")
except:
    logger.info('File spain_data.csv not found, downloading...')
    data_fetcher.spain.update_data()

# Get the data
column_names = ['casos_total', 'altas',
                'fallecimientos', 'ingresos_uci', 'hospitalizados']
url = 'https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/nacional_covid19.csv'

logger.info('Reading data...')
df_spain = pd.read_csv('data/spain_data.csv', delimiter=',',
    parse_dates=['fecha'], date_parser=date_parse_spain)
df_malaga = pd.read_csv('data/malaga_data.csv', delimiter=',',
    parse_dates=['fecha'], date_parser=date_parse_malaga)
logger.info('Data read sucessfully.')

for column_name in column_names:
    df_spain[column_name] = df_spain[column_name].astype('int')
    df_malaga[column_name] = df_malaga[column_name].astype('int')


# Data transformations
def moving_average(data, n=7):
    averages = [0 for i in range(n)]
    data = list(data)
    size = len(data)
    for i in range(7, size):
        averages.append(sum(data[i-7:i])/n)
    return averages

logger.info('Computing metrics for plot.')
# Compute data
# Spain
cases_spain = df_spain['casos_total']
cured_spain = df_spain['altas']
deaths_spain = df_spain['fallecimientos']
active_spain = df_spain['casos_total'] - \
    df_spain['altas'] - df_spain['fallecimientos']

diff_active_spain = np.insert(np.diff(active_spain), 0, 0)
diff_cases_spain = np.insert(np.diff(cases_spain), 0, 0)
diff_deaths_spain = np.insert(np.diff(deaths_spain), 0, 0)

# Málaga
cases_malaga = df_malaga['casos_total']
cured_malaga = df_malaga['altas']
deaths_malaga = df_malaga['fallecimientos']
active_malaga = df_malaga['casos_total'] - \
    df_malaga['altas'] - df_malaga['fallecimientos']

diff_active_malaga = np.insert(np.diff(active_malaga), 0, 0)
diff_cases_malaga = np.insert(np.diff(cases_malaga), 0, 0)
diff_deaths_malaga = np.insert(np.diff(deaths_malaga), 0, 0)


# Plot the data
logger.info('Data ready for plotting.')
logger.info('Starting plotting.')


# Fix pandas and matplotlib datetime
pd.plotting.register_matplotlib_converters()

plt.style.use('seaborn-pastel')

fig, ax = plt.subplots(figsize=(30, 20))

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Product Sans'

plt.rcParams['axes.edgecolor'] = '#212121'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.color'] = '#212121'
plt.rcParams['ytick.color'] = '#212121'


# ----------------------------------------------------------------
ax = plt.subplot(221)

ax.set_axisbelow(True)
plt.grid(color='#DDDDDD', linestyle='-', linewidth=0.8, axis='y')

ax.set_title('Accumulated actives, deaths and recovered', fontsize=20)

plt.tick_params(axis='x', which='major', labelsize=15)
plt.tick_params(axis='y', which='both', left=False, right=False, labelsize=15)

ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['bottom'].set_smart_bounds(True)

data_colors = ['#001b3f', '#05638f', '#6eaedf', '#d00005']

ax.bar(df_spain['fecha'], active_spain, label='Actives', color=data_colors[0])
ax.bar(df_spain['fecha'], deaths_spain, label='Deaths',
       color=data_colors[1], bottom=active_spain)
ax.bar(df_spain['fecha'], cured_spain, label='Recovered',
       color=data_colors[2], bottom=active_spain+deaths_spain)

ax.legend()

ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))


# ----------------------------------------------------------------
ax = plt.subplot(222)

ax.set_axisbelow(True)
plt.grid(color='#DDDDDD', linestyle='-', linewidth=0.8, axis='y')

ax.set_title('Accumulated actives, deaths and recovered (Málaga)', fontsize=20)


plt.tick_params(axis='x', which='major', labelsize=15)
plt.tick_params(axis='y', which='both', left=False, right=False, labelsize=15)

ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['bottom'].set_smart_bounds(True)


ax.bar(df_malaga['fecha'], active_malaga,
       label='Actives', color=data_colors[0])
ax.bar(df_malaga['fecha'], deaths_malaga,
       label='Deaths', color=data_colors[1], bottom=active_malaga)
ax.bar(df_malaga['fecha'], cured_malaga,
       label='Recovered', color=data_colors[2], bottom=active_malaga + deaths_malaga)

ax.legend()

ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))


# ----------------------------------------------------------------
ax = plt.subplot(223)

ax.set_axisbelow(True)
plt.grid(color='#EEEEEE', linestyle='-', linewidth=0.8, axis='y')

ax.set_title('Active cases variation', fontsize=20)

plt.tick_params(axis='x', which='major', labelsize=15)
plt.tick_params(axis='y', which='both', left=False, right=False, labelsize=15)

ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['bottom'].set_smart_bounds(True)

ax.plot(df_spain['fecha'], [0] * len(df_spain['fecha']),
        color='212121', lw='2', linestyle=':')
ax.bar(df_spain['fecha'], diff_active_spain, lw=2.5,
       color=data_colors[0], label='Actives variation')


ax.plot(df_spain['fecha'], moving_average(diff_active_spain), lw=2.5,
        color=data_colors[3], label='Moving average of actives variation')

ax.legend(loc='upper left')

ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))


# ----------------------------------------------------------------
ax = plt.subplot(224)

ax.set_axisbelow(True)
plt.grid(color='#EEEEEE', linestyle='-', linewidth=0.8, axis='y')

ax.set_title('Active cases variation (Málaga)', fontsize=20)

plt.tick_params(axis='x', which='major', labelsize=15)
plt.tick_params(axis='y', which='both', left=False, right=False, labelsize=15)

ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['bottom'].set_smart_bounds(True)

ax.plot(df_malaga['fecha'], [0] * len(df_malaga['fecha']),
        color='212121', lw='2', linestyle=':')
ax.bar(df_malaga['fecha'], diff_active_malaga, lw=2.5,
       color=data_colors[0], label='Actives variation')

ax.plot(df_malaga['fecha'], moving_average(diff_active_malaga), lw=2.5,
        color=data_colors[3], label='Moving average of actives variation')

ax.legend(loc='upper left')

ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))


# ----------------------------------------------------------------
fig.text(0.13, 0.06, "Data source: https://github.com/datadista/datasets"
                     "\nAuthor: Oleg Brezitskyy (@oleg.brz)", fontsize=10)

logger.info('Writing plot to image.')
plt.savefig('plot.png', dpi=300, bbox_inches='tight')

logger.info('Plot written sucessfully.')
