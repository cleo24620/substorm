import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt

import config

# fp_omni = "data/omni/days/2019-12-31.asc"  # modify
# fp_supermag = "data/supermag/days/data_2019-12-31.csv"
# fp_omni_substorm = "data/omni/substorm_list_statistics/2019-12-31.csv"
# fp_supermag_substorm = "data/supermag/substorm_list_statistics/data_2019-12-31.csv"
# day_start_time = pd.Timestamp('2019-12-31 00:00:00')
fp_omni = "data/omni/days/2015-01-07.asc"  # modify
fp_supermag = "data/supermag/days/data_2015-01-07.csv"
fp_omni_substorm = "data/omni/substorm_list_statistics/2015-01-07.csv"
fp_supermag_substorm = "data/supermag/substorm_list_statistics/data_2015-01-07.csv"
day_start_time = pd.Timestamp('2015-01-07 00:00:00')

df_omni = pd.read_csv(fp_omni, index_col=0)
df_omni.index = pd.to_datetime(df_omni.index)
df_supermag = pd.read_csv(fp_supermag, index_col=0)
df_supermag.index = pd.to_datetime(df_supermag.index)

df_omni_substorm = pd.read_csv(fp_omni_substorm)
df_supermag_substorm = pd.read_csv(fp_supermag_substorm)
for column_name in config.SUBSTORM_COLUMN_NAMES:
    df_omni_substorm[column_name] = pd.to_datetime(df_omni_substorm[column_name])
    df_supermag_substorm[column_name] = pd.to_datetime(df_supermag_substorm[column_name])

fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(12, 8))

axes[0].plot(df_omni.index, df_omni['IMF_GSM_Bz'] * 10, label="IMF_GSM_Bz * 10")
axes[0].plot(df_omni.index, df_omni['AU'], label="AU")
axes[0].plot(df_omni.index, df_omni['AL'], label="AL")
axes[0].plot(df_omni.index, df_omni['AE'], label="AE")
axes[0].axhline(0, linestyle="-", color="black")

axes[0].set_title("Auroral")
axes[0].legend()

axes[1].plot(df_supermag.index, df_supermag['GSM_Bz'] * 10)
axes[1].plot(df_supermag.index, df_supermag['SMU'], label="SMU")
axes[1].plot(df_supermag.index, df_supermag['SML'], label="SML")
axes[1].plot(df_supermag.index, df_supermag['SME'], label="SME")
axes[1].axhline(0, linestyle="-", color="black")
axes[1].set_title("SuperMAG")
axes[1].set_xlabel("Time (Hour)")
axes[1].legend()

colors = {'growth': 'red', 'expansion': 'blue', 'recovery': 'green'}
alpha = 0.2
for ax, df in zip(axes, [df_omni_substorm, df_supermag_substorm]):
    for _, row in df.iterrows():
        if row[config.SUBSTORM_COLUMN_NAMES[0]] is not pd.NaT:
            ax.axvspan(row[config.SUBSTORM_COLUMN_NAMES[0]], row[config.SUBSTORM_COLUMN_NAMES[1]],
                       color=colors['growth'], alpha=alpha)
        if row[config.SUBSTORM_COLUMN_NAMES[2]] is not pd.NaT:
            ax.axvspan(row[config.SUBSTORM_COLUMN_NAMES[2]], row[config.SUBSTORM_COLUMN_NAMES[3]],
                       color=colors['expansion'], alpha=alpha)
        if row[config.SUBSTORM_COLUMN_NAMES[4]] is not pd.NaT:
            ax.axvspan(row[config.SUBSTORM_COLUMN_NAMES[4]], row[config.SUBSTORM_COLUMN_NAMES[5]],
                       color=colors['recovery'], alpha=alpha)
axes[0].text(0.05, 0.8, "growth: red\nexpansion: blue\nrecovery: green", transform=axes[0].transAxes, color='blue')

xlim_start = day_start_time
xlim_end = day_start_time + pd.Timedelta(days=1)
axes[0].set_xlim(xlim_start, xlim_end)

time_formatter = mdates.DateFormatter('%H')
axes[1].xaxis.set_major_formatter(time_formatter)
axes[1].xaxis.set_major_locator(mdates.HourLocator(interval=1))

fig.suptitle(
    f"Comparison of substorm phases based on auroral and supermag data ({df_omni.index[0].strftime("%Y-%m-%d %H:%M")} to {df_omni.index[-1].strftime("%H:%M")})")

plt.show()
