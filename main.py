import malaga_data.csv_converter as madata
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler('log_file.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


# Get the data
column_names = ['casos', 'altas', 'fallecimientos', 'ingresos_uci', 'hospitalizados']
url = 'https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/nacional_covid19.csv'

logger.info('Getting data from GitHub.')
df_spain = pd.read_csv(url, delimiter=',', parse_dates=['fecha'])
logger.info('Success.')
df_spain = df_spain.fillna(0)

for column_name in column_names:
    df_spain[column_name] = df_spain[column_name].astype('int')

madata.update_data()
madata.generate_csv()

df_malaga_path = './data_malaga.csv'

dateparse = lambda x: pd.datetime.strptime(x, '%d/%m/%Y')
df_malaga = pd.read_csv(df_malaga_path, delimiter=',', parse_dates=['fecha'], date_parser=dateparse)
df_malaga = df_malaga.fillna(0)

for column_name in column_names:
    df_spain[column_name] = df_spain[column_name].astype('int')

logger.info('Computing data for plot.')
# Compute data

# Spain
cases_spain = df_spain['casos']
cured_spain = df_spain['altas']
deaths_spain = df_spain['fallecimientos']
active_spain = df_spain['casos'] - df_spain['altas'] - df_spain['fallecimientos']

diff_active_spain = np.insert(np.diff(active_spain), 0, 0)
diff_cases_spain = np.insert(np.diff(cases_spain), 0, 0)
diff_deaths_spain = np.insert(np.diff(deaths_spain), 0, 0)

# Málaga
cases_malaga = df_malaga['casos']
cured_malaga = df_malaga['altas']
deaths_malaga = df_malaga['fallecimientos']
active_malaga = df_malaga['casos'] - df_malaga['altas'] - df_malaga['fallecimientos']

diff_active_malaga = np.insert(np.diff(active_malaga), 0, 0)
diff_cases_malaga = np.insert(np.diff(cases_malaga), 0, 0)
diff_deaths_malaga = np.insert(np.diff(deaths_malaga), 0, 0)

logger.info('Data ready for plotting.')

logger.info('Starting plotting.')
# Plot the data

pd.plotting.register_matplotlib_converters()

plt.style.use('seaborn-pastel')

fig, ax = plt.subplots(figsize=(30,20))

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Product Sans'

plt.rcParams['axes.edgecolor']='#212121'
plt.rcParams['axes.linewidth']=0.8
plt.rcParams['xtick.color']='#212121'
plt.rcParams['ytick.color']='#212121'

# ----------------------------------------------------------------

ax = plt.subplot(221)

ax.set_axisbelow(True)
plt.grid(color= '#DDDDDD', linestyle='-', linewidth=0.8, axis='y')

ax.set_title('Accumulated actives, deaths and recovered', fontsize=20)

plt.tick_params(axis='x', which='major', labelsize=15)
plt.tick_params(axis='y', which='both', left=False, right=False, labelsize=15)

ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['bottom'].set_smart_bounds(True)

data_colors = ['#001b3f', '#05638f', '#6eaedf']

ax.bar(df_spain['fecha'], active_spain, label='Actives', color = data_colors[0])
ax.bar(df_spain['fecha'], deaths_spain, label='Deaths', color=data_colors[1], bottom=active_spain)
ax.bar(df_spain['fecha'], cured_spain, label='Recovered', color = data_colors[2], bottom=active_spain+deaths_spain)

ax.legend()

ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

# ----------------------------------------------------------------

ax = plt.subplot(222)

ax.set_axisbelow(True)
plt.grid(color= '#DDDDDD', linestyle='-', linewidth=0.8, axis='y')

ax.set_title('Accumulated actives, deaths and recovered (Málaga)', fontsize=20)


plt.tick_params(axis='x', which='major', labelsize=15)
plt.tick_params(axis='y', which='both', left=False, right=False, labelsize=15)

ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['bottom'].set_smart_bounds(True)

data_colors = ['#001b3f', '#05638f', '#6eaedf']

ax.bar(df_malaga['fecha'], active_malaga,
       label='Actives', color = data_colors[0])
ax.bar(df_malaga['fecha'], deaths_malaga,
       label='Deaths', color=data_colors[1], bottom=active_malaga)
ax.bar(df_malaga['fecha'], cured_malaga,
       label='Recovered', color = data_colors[2], bottom = active_malaga + deaths_malaga)

ax.legend()

ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

# ----------------------------------------------------------------

ax = plt.subplot(223)

ax.set_axisbelow(True)
plt.grid(color= '#EEEEEE', linestyle='-', linewidth=0.8, axis='y')

ax.set_title('Active cases variation', fontsize=20)

plt.tick_params(axis='x', which='major', labelsize=15)
plt.tick_params(axis='y', which='both', left=False, right=False, labelsize=15)

ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['bottom'].set_smart_bounds(True)

ax.plot(df_spain['fecha'], [0] * len(df_spain['fecha']), color='212121', lw='2', linestyle=':')
ax.bar(df_spain['fecha'], diff_active_spain, lw=2.5, color= data_colors[0], label='Actives variation')

ax.legend(loc='upper left')

ax.annotate('Oopsie from\nthe Government', xy=(df_spain['fecha'][52], diff_active_spain[52]), xytext=(-20,40),
            textcoords='offset points', va='center', ha='center', color='#000000',
            fontsize=10, arrowprops={'arrowstyle': '->'})

ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

# ----------------------------------------------------------------

ax = plt.subplot(224)

ax.set_axisbelow(True)
plt.grid(color= '#EEEEEE', linestyle='-', linewidth=0.8, axis='y')

ax.set_title('Active cases variation (Málaga)', fontsize=20)

plt.tick_params(axis='x', which='major', labelsize=15)
plt.tick_params(axis='y', which='both', left=False, right=False, labelsize=15)

ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['bottom'].set_smart_bounds(True)

ax.plot(df_malaga['fecha'], [0] * len(df_malaga['fecha']), color='212121', lw='2', linestyle=':')
ax.bar(df_malaga['fecha'], diff_active_malaga, lw=2.5, color= data_colors[0], label='Actives variation')

ax.legend(loc='upper left')

ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

# ----------------------------------------------------------------

fig.text(0.13, 0.06, "Data source: https://github.com/datadista/datasets"
                     "\nAuthor: Oleg Brezitskyy (@oleg.brz)", fontsize=10) 

logger.info('Writing plot  to image.')
plt.savefig('plot.png', dpi=300, bbox_inches='tight')

logger.info('Done.')
