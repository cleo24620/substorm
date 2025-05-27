import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt

import config

fp = "data/supermag/days/data_2019-12-31.csv"
fp_substorm = "data/supermag/substorm_list_statistics/data_2019-12-31.csv"
day_start_time = pd.Timestamp('2019-12-31 00:00:00')
# fp = "data/supermag/days/data_2018-08-26.csv"
# fp_substorm = "data/supermag/substorm_list_statistics/data_2018-08-26.csv"
# day_start_time = pd.Timestamp('2018-08-26 00:00:00')

df = pd.read_csv(fp, index_col=0)
df.index = pd.to_datetime(df.index)

df_substorm = pd.read_csv(fp_substorm)
for column_name in config.SUBSTORM_COLUMN_NAMES:
    df_substorm[column_name] = pd.to_datetime(df_substorm[column_name])

fig, ax = plt.subplots(figsize=(12, 4))

plt.plot(df.index, df['GSM_Bz'] * 10)
plt.plot(df.index, df['SMU'], label="SMU")
plt.plot(df.index, df['SML'], label="SML")
plt.plot(df.index, df['SME'], label="SME")
plt.axhline(0, linestyle="-", color="black")
plt.title(
    f"substorm phases based on supermag data ({df.index[0].strftime("%Y-%m-%d %H:%M")} to {df.index[-1].strftime("%H:%M")})")
plt.xlabel("Time (Hour)")
plt.legend()

colors = {'growth': 'red', 'expansion': 'blue', 'recovery': 'green'}
alpha = 0.2
for _, row in df_substorm.iterrows():
    if row[config.SUBSTORM_COLUMN_NAMES[0]] is not pd.NaT:
        plt.axvspan(row[config.SUBSTORM_COLUMN_NAMES[0]], row[config.SUBSTORM_COLUMN_NAMES[1]],
                    color=colors['growth'], alpha=alpha)
    if row[config.SUBSTORM_COLUMN_NAMES[2]] is not pd.NaT:
        plt.axvspan(row[config.SUBSTORM_COLUMN_NAMES[2]], row[config.SUBSTORM_COLUMN_NAMES[3]],
                    color=colors['expansion'], alpha=alpha)
    if row[config.SUBSTORM_COLUMN_NAMES[4]] is not pd.NaT:
        plt.axvspan(row[config.SUBSTORM_COLUMN_NAMES[4]], row[config.SUBSTORM_COLUMN_NAMES[5]],
                    color=colors['recovery'], alpha=alpha)
plt.text(0.05, 0.8, "growth: red\nexpansion: blue\nrecovery: green", transform=ax.transAxes, color='blue')

xlim_start = day_start_time
xlim_end = day_start_time + pd.Timedelta(days=1)
plt.xlim(xlim_start, xlim_end)

time_formatter = mdates.DateFormatter('%H')
ax.xaxis.set_major_formatter(time_formatter)
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

plt.show()
