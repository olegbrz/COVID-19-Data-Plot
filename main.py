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


def update_csv_if_needed(csv_path, update_function):
    file_name = csv_path.split('/')[-1]
    try:
        if time() - getmtime(csv_path) > (30 * 60):
            logger.info(f'Updating {file_name}...')
            update_function()
        else:
            logger.info(
                f'File {file_name} is recent, won\'t be updated.')
    except:
        logger.info(f'File {file_name} not found, downloading...')
        update_function()


update_csv_if_needed('data/malaga_data.csv', data_fetcher.malaga.update_data)
update_csv_if_needed('data/spain_data.csv', data_fetcher.spain.update_data)

# Get the data

logger.info('Reading data...')
df_spain = pd.read_csv('data/spain_data.csv', delimiter=',',
                       parse_dates=['fecha'], date_parser=date_parse_spain)
df_malaga = pd.read_csv('data/malaga_data.csv', delimiter=',',
                        parse_dates=['fecha'], date_parser=date_parse_malaga)
logger.info('Data read sucessfully.')

column_names = ['casos_total', 'altas',
                'fallecimientos', 'ingresos_uci', 'hospitalizados']

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


# Data join
data = {
    'Spain': {
        'date': df_spain['fecha'],
        'actives': active_spain,
        'actives difference': diff_active_spain,
        'deaths': deaths_spain,
        'cured': cured_spain,
    },
    'Málaga': {
        'date': df_malaga['fecha'],
        'actives': active_malaga,
        'actives difference': diff_active_malaga,
        'deaths': deaths_malaga,
        'cured': cured_malaga
    }
}


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

n = 0
data_colors = ['#001b3f', '#05638f', '#6eaedf', '#d00005']


def plot_init():
    global n
    n += 1
    ax = plt.subplot(220 + n)
    ax.set_axisbelow(True)
    plt.grid(color='#DDDDDD', linestyle='-', linewidth=0.8, axis='y')
    plt.tick_params(axis='x', which='major', labelsize=15)
    plt.tick_params(axis='y', which='both', left=False,
                    right=False, labelsize=15)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['bottom'].set_smart_bounds(True)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    return ax


def accumulated_plot(location):
    ax = plot_init()
    ax.set_title(
        f'Accumulated actives, deaths and recovered ({location})', fontsize=20)
    # Data extraction
    date = data[location]['date']
    actives = data[location]['actives']
    deaths = data[location]['deaths']
    cured = data[location]['cured']
    # ------------------------------------
    ax.bar(date, actives,
           label='Actives', color=data_colors[0])
    ax.bar(date, deaths,
           label='Deaths', color=data_colors[1], bottom=actives)
    ax.bar(date, cured,
           label='Cured', color=data_colors[2], bottom=actives+deaths)
    ax.legend(loc='upper left')


def variation_plot(location):
    ax = plot_init()
    ax.set_title(f'Active cases variation ({location})', fontsize=20)
    # Data extraction
    date = data[location]['date']
    actives_difference = data[location]['actives difference']
    # ------------------------------------
    ax.plot(date, [0] * len(date),
            color='212121', lw='2', linestyle=':')
    ax.bar(date, actives_difference, lw=2.5,
           color=data_colors[0], label='Actives variation')
    ax.plot(date, moving_average(actives_difference), lw=2.5,
            color=data_colors[3], label='Moving average of actives variation')
    ax.legend(loc='upper left')


# ----------------------------------------------------------------
accumulated_plot('Spain')
# ----------------------------------------------------------------
accumulated_plot('Málaga')
# ----------------------------------------------------------------
variation_plot('Spain')
# ----------------------------------------------------------------
variation_plot('Málaga')
# ----------------------------------------------------------------

fig.text(0.13, 0.06, "Data source: https://github.com/datadista/datasets"
                     "\nAuthors: Oleg Brezitskyy (@olegbrz), Rubén Jiménez (@rubenjr0)",
                     fontsize=10)

logger.info('Writing plot to image.')
plt.savefig('plot.png', dpi=300, bbox_inches='tight')

logger.info('Plot written sucessfully.')
