import json
import time
from pathlib import Path
from typing import Optional

import pandas as pd

import config


def get_duration(fp: str, sdir: Optional[str] = None):
    fp = Path(fp)
    df = pd.read_csv(fp)
    for column_name in config.SUBSTORM_COLUMN_NAMES:
        df[column_name] = pd.to_datetime(df[column_name])
    i = 0
    for column_name in config.SUBSTORM_PHASE_DURATION_NAMES:
        df[column_name] = df.iloc[:, i + 1] - df.iloc[:, i]
        i += 2
    df[config.SUBSTORM_DURATION_NAME] = df[config.SUBSTORM_PHASE_DURATION_NAMES].sum(axis=1)
    if sdir:
        sdir = Path(sdir)
        sdir.mkdir(parents=True, exist_ok=True)
        sfn = fp.name
        sfp = sdir / sfn
        print("---")
        print(f"Save {sfn}")
        df.to_csv(sfp, index=False)
        print(f"Saved {sfn}")
        print("---")
    return df


# fp = "data/supermag/substorm_list/data_1995-03-10.csv"
# get_duration("data/supermag/substorm_list/data_1995-03-10.csv", sdir=config.OMNI_SUBSTORM_DURATION_DIR)

# Get omni substorm duration
print("---")
print("Get OMNI substorm duration:")
st = time.perf_counter()
for fp in config.OMNI_SUBSTORM_LIST_STATS_DIR.iterdir():
    sdir = config.OMNI_SUBSTORM_DURATION_DIR
    sfp = Path(sdir) / Path(fp.name)
    if not sfp.exists():
        get_duration(fp, sdir=config.OMNI_SUBSTORM_DURATION_DIR)
et = time.perf_counter()
print(f"Successfully get, cost {et - st:.6f} seconds.")

# Get supermag substorm duration
print("---")
print("Get SuperMAG substorm duration:")
st = time.perf_counter()
for fp in config.SUPERMAG_SUBSTORM_LIST_STATS_DIR.iterdir():
    sdir = config.SUPERMAG_SUBSTORM_DURATION_DIR
    sfp = Path(sdir) / Path(fp.name)
    if not sfp.exists():
        get_duration(fp, sdir=config.SUPERMAG_SUBSTORM_DURATION_DIR)
et = time.perf_counter()
print(f"Successfully get, cost {et - st:.6f} seconds.")

# Get OMNI substorm phase durations average
print("---")
print("Get OMNI substorm durations average:")
st = time.perf_counter()
if not config.OMNI_STATS_AVERAGE_FP.exists():
    _list = config.SUBSTORM_PHASE_DURATION_NAMES
    _list.append(config.SUBSTORM_DURATION_NAME)
    growth_durations = []
    expansion_durations = []
    recovery_durations = []
    substorm_durations = []
    substorm_duration_ratios = []
    for fp in config.OMNI_SUBSTORM_DURATION_DIR.iterdir():
        df = pd.read_csv(fp)
        for column_name in _list:
            df[column_name] = pd.to_timedelta(df[column_name])
        for column_name, duration_list in zip(config.SUBSTORM_PHASE_DURATION_NAMES,
                                              [growth_durations, expansion_durations, recovery_durations]):
            duration_average = df[column_name].mean()
            if duration_average is not pd.NaT:
                duration_list.append(duration_average)
        duration_average = df[config.SUBSTORM_DURATION_NAME].mean()
        if duration_average is not pd.NaT:
            substorm_durations.append(duration_average)
            substorm_duration_ratios.append(df[config.SUBSTORM_DURATION_NAME].sum() / pd.Timedelta(days=1))
    _dict = {}
    for _list, _key in zip(
            [growth_durations, expansion_durations, recovery_durations, substorm_durations],
            config.DURATIONS_AVERAGE_NAMES):
        _dict[_key] = pd.Series(_list).mean()
        _dict[_key] = str(_dict[_key])
    _dict[config.RATIOS_AVERAGE_NAME] = sum(substorm_duration_ratios) / len(substorm_duration_ratios)
    with open(config.OMNI_STATS_AVERAGE_FP, 'w') as f:
        print("Save OMNI substorm duration average stats as json file:")
        json.dump(_dict, f, indent=4)
        print("Successfully save.")
et = time.perf_counter()
print(
    f"Successfully get OMNI substorm durations average statistics, and save them as json file. Cost {et - et:.6f} seconds.")
print("---")

# Get SuperMAG substorm phase durations average
print("---")
print("Get SuperMAG substorm durations average:")
st = time.perf_counter()
if not config.SUPERMAG_STATS_AVERAGE_FP.exists():
    _list = config.SUBSTORM_PHASE_DURATION_NAMES
    _list.append(config.SUBSTORM_DURATION_NAME)
    growth_durations = []
    expansion_durations = []
    recovery_durations = []
    substorm_durations = []
    substorm_duration_ratios = []
    for fp in config.SUPERMAG_SUBSTORM_DURATION_DIR.iterdir():
        df = pd.read_csv(fp)
        for column_name in _list:
            df[column_name] = pd.to_timedelta(df[column_name])
        for column_name, duration_list in zip(config.SUBSTORM_PHASE_DURATION_NAMES,
                                              [growth_durations, expansion_durations, recovery_durations]):
            duration_average = df[column_name].mean()
            if duration_average is not pd.NaT:
                duration_list.append(duration_average)
        duration_average = df[config.SUBSTORM_DURATION_NAME].mean()
        if duration_average is not pd.NaT:
            substorm_durations.append(duration_average)
            substorm_duration_ratios.append(df[config.SUBSTORM_DURATION_NAME].sum() / pd.Timedelta(days=1))
    _dict = {}
    for _list, _key in zip(
            [growth_durations, expansion_durations, recovery_durations, substorm_durations],
            config.DURATIONS_AVERAGE_NAMES):
        _dict[_key] = pd.Series(_list).mean()
        _dict[_key] = str(_dict[_key])
    _dict[config.RATIOS_AVERAGE_NAME] = sum(substorm_duration_ratios) / len(substorm_duration_ratios)
    with open(config.SUPERMAG_STATS_AVERAGE_FP, 'w') as f:
        print("Save SuperMAG substorm duration average stats as json file:")
        json.dump(_dict, f, indent=4)
        print("Successfully save.")
et = time.perf_counter()
print(
    f"Successfully get SuperMAG substorm durations average statistics, and save them as json file. Cost {et - et:.6f} seconds.")
print("---")
