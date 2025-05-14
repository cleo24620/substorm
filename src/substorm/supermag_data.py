import json
import time

file_st = time.perf_counter()

from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    SME_FILEPATH,
    SMU_SML_FILEPATH,
    SUPERMAG_IMFB_FILEPATH,
    SUPERMAG_IMFBz_FILL_VALUE,
    SME_FILL_VALUE,
    SML_FILL_VALUE,
    SMU_FILL_VALUE,
)

# sme
start_time = time.perf_counter()
print("Start process sme")
df_sme = pd.read_csv(SME_FILEPATH)
df_sme["SME"] = df_sme["SME"].replace(SME_FILL_VALUE, np.nan)
end_time = time.perf_counter()
duration = end_time - start_time
print(f"End process sme, cost {duration:.6f} seconds\n")

# smu_sml
print("Start process smu_sml")
start_time = time.perf_counter()
df_smu_sml = pd.read_csv(SMU_SML_FILEPATH)
df_smu_sml["SMU"] = df_smu_sml["SMU"].replace(SMU_FILL_VALUE, np.nan)
df_smu_sml["SML"] = df_smu_sml["SML"].replace(SML_FILL_VALUE, np.nan)
end_time = time.perf_counter()
duration = end_time - start_time
print(f"End process smu_sml, cost {duration:.6f} seconds\n")

# imf bz
print("Start process imf bz")
start_time = time.perf_counter()
df_imf_bz = pd.read_csv(SUPERMAG_IMFB_FILEPATH)
df_imf_bz["GSM_Bz"] = df_imf_bz["GSM_Bz"].replace(SUPERMAG_IMFBz_FILL_VALUE, np.nan)
end_time = time.perf_counter()
duration = end_time - start_time
print(f"End process imf bz, cost {duration:.6f} seconds.\n")

# Check if the datetime columns of imfbz, sme, smu_sml DataFrames are identical.
are_datetime_columns_identical = df_imf_bz["Date_UTC"].equals(
    df_sme["Date_UTC"]
) and df_sme["Date_UTC"].equals(df_smu_sml["Date_UTC"])
assert are_datetime_columns_identical

# Concatenate the multiple DataFrames mentioned above by columns, making sure to keep only one datetime column.
df = pd.concat(
    [df_imf_bz[["Date_UTC", "GSM_Bz"]], df_sme["SME"], df_smu_sml[["SMU", "SML"]]],
    axis=1,
)

# The string-type datetime column in the concatenated DataFrame is converted to the pd.Timestamp type.
df["Date_UTC"] = pd.to_datetime(df["Date_UTC"])

# Set this datetime column as the index.
df.set_index("Date_UTC", inplace=True)

# Save some statistical data.
describe_stats = df.describe()
describe_stats.loc["nan_counts"] = df.isna().sum()  ## add 'nan' row
save_filepath = Path("./data/supermag/describe_stats.csv")
if not save_filepath.exists():
    describe_stats.to_csv(save_filepath)
    print(f"Save File '{save_filepath}' successfully.\n")
else:
    print(f"File '{save_filepath} already exists. Skipping save.\n")

## Differentiate the selected columns (sml) with respect to time, with a time resolution of 1 minute.
## Take all negative values of the result data and find the median.
sml_derivatives = df["SML"].diff()
neg_sml_derivatives = sml_derivatives[sml_derivatives < 0]
neg_sml_derivatives_median_dict = {
    "neg_sml_derivatives_median": neg_sml_derivatives.median()
}
save_filepath = Path("./data/supermag/negative_sml_derivatives.json")
if not save_filepath.exists():
    with open(save_filepath, "w") as f:
        json.dump(neg_sml_derivatives_median_dict, f, indent=4)
    print(f"Save File '{save_filepath}' successfully.\n")
else:
    print(f"File '{save_filepath} already exists. Skipping save.\n")

# Group this DataFrame by months and then save the resulting DataFrame for each month as both pkl and csv files.
## Filepaths
output_base_dir = Path("./data/supermag/months")
pkl_dir = output_base_dir / "pkl_files"
csv_dir = output_base_dir / "csv_files"
pkl_dir.mkdir(parents=True, exist_ok=True)
csv_dir.mkdir(parents=True, exist_ok=True)
print(f"Pkl files will save to {pkl_dir}")
print(f"Csv files will save to {csv_dir}")

## Group
start_time = time.perf_counter()
print(
    "Group the Dataframe by month and save the corresponding month DataFrames to pkl and csv files."
)
grouped_by_month = df.groupby(df.index.to_period("M"))
for month_period, month_df in grouped_by_month:
    month_period: pd.Period
    month_period_strftime = month_period.strftime("%Y-%m")
    pkl_filename = f"data_{month_period_strftime}.pkl"
    csv_filename = f"data_{month_period_strftime}.csv"
    pkl_filepath = pkl_dir / pkl_filename
    csv_filepath = csv_dir / csv_filename
    if month_df.empty:
        print(f"The DataFrame of month {month_period_strftime} is empty, skip saving.")
    else:
        if not pkl_filepath.exists():
            print(
                f"Process month: {month_period_strftime}, lines of DataFrame is {len(month_df)}."
            )
            try:
                month_df.to_pickle(pkl_filepath)
                print(f"Save {pkl_filepath} successfully")
            except Exception as e:
                print(f"Failed to save {pkl_filepath}, error is {e}")
        else:
            print(f"File {pkl_filepath} already exists. Skipping save.")
        if not csv_filepath.exists():
            try:
                month_df.to_csv(csv_filepath)
                print(f"Save {csv_filepath} successfully")
            except Exception as e:
                print(f"Failed to save {csv_filepath}, error is {e}")
        else:
            print(f"File {csv_filepath} already exists. Skipping save.")
end_time = time.perf_counter()
duration = end_time - start_time
print(f"End grouping process, cost {duration:.6f} seconds.\n")

file_et = time.perf_counter()
file_duration = file_et - file_st
print(f"End the whole file, cost {file_duration:.6f} seconds")
