"""
Time resolution: 1 minute;
Time resolution of derivatives: 1 minute;
"""

import json
from pathlib import Path

import pandas as pd

# crawler
HRO_MODIFIED_URL_Y = "https://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/modified/"  # url of the year file
HRO_MODIFIED_URL_M = "https://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/modified/monthly_1min/"  # url of the month file
HTML_TAG_M = "a"
HREF_PATTERN_M = r"omni_min\d{6}.asc"  # regular expression pattern

# variables
HRO_1M_MODIFIED_VARS = ["Year", "Day", "Hour", "Minute", "ID for IMF spacecraft", "ID for SW Plasma spacecraft",
                        "# of points in IMF averages", "# of points in Plasma averages", "Percent interp",
                        "Timeshift, sec",
                        "RMS, Timeshift", "RMS, Phase front normal", "Time btwn observations, sec",
                        "Field magnitude average, nT",
                        "Bx, nT (GSE, GSM)", "By, nT (GSE)", "Bz, nT (GSE)", "By, nT (GSM)", "Bz, nT (GSM)",
                        "RMS SD B scalar, nT",
                        "RMS SD field vector, nT", "Flow speed, km/s", "Vx Velocity, km/s, GSE",
                        "Vy Velocity, km/s, GSE",
                        "Vz Velocity, km/s, GSE", "Proton Density, n/cc", "Temperature, K", "Flow pressure, nPa",
                        "Electric field, mV/m",
                        "Plasma beta", "Alfven mach number", "X(s/c), GSE, Re", "Y(s/c), GSE, Re", "Z(s/c), GSE, Re",
                        "BSN location, Xgse, Re", "BSN location, Ygse, Re", "BSN location, Zgse, Re", "AE-index, nT",
                        "AL-index, nT",
                        "AU-index, nT", "SYM/D index, nT", "SYM/H index, nT", "ASY/D index, nT", "ASY/H index, nT",
                        "PC(N) index",
                        "Na/Np Ratio", "Magnetosonic mach number", ]  # vars of hro 1 minute modified version file
SELECTED_VARS = ["Year", "Day", "Hour", "Minute", "Bz, nT (GSM)", "AE-index, nT", "AL-index, nT", "AU-index, nT", ]
SELECTED_VARS_RENAMES = {'Bz, nT (GSM)': 'IMF_GSM_Bz', 'AE-index, nT': 'AE', 'AL-index, nT': 'AL', 'AU-index, nT': 'AU'}
SUPERMAG_VARS = ["Date_UTC", "SME", "SMU", "SML", "GSM_Bz"]

# fill values
HRO1_VARS_FILL_VALUE = {"IMF_GSM_Bz": 9999.99, "AE": 99999, "AL": 99999, "AU": 99999}
SME_FILL_VALUE = 999999.0
SMU_FILL_VALUE = SML_FILL_VALUE = 999999
SUPERMAG_IMFBz_FILL_VALUE = 999999.0
MAX_NAN_RATIO = 0.1

# filenames
OMNI_DATA_DIR = Path("./data/omni")
OMNI_ORIGINAL_DATA_DIR = OMNI_DATA_DIR / 'original'
OMNI_ORIGINAL_DATA_SEP = r"\s+"
OMNI_ORIGINAL_DATA_PREFIX = 'omni_min'
OMNI_ORIGINAL_DATA_EXTENSION = 'asc'
OMNI_PROCESSED_DATA_DIR = OMNI_DATA_DIR / 'processed'
OMNI_PROCESSED_DATA_PREFIX = 'processed'
OMNI_PROCESSED_DATA_EXTENSIONS = ['pkl', 'csv']
OMNI_START_YEAR = 1995
OMNI_START_MONTH = 1
OMNI_START_DAY = 1
OMNI_END_YEAR = 2024
OMNI_END_MONTH = 8
OMNI_END_DAY = 31
SUPERMAG_DATA_DIR = Path("./data/supermag")
SME_FILEPATH = SUPERMAG_DATA_DIR / "supermag_electrojet_index_one_miniut_all_years.csv"
SMU_SML_FILEPATH = (SUPERMAG_DATA_DIR / "supermag_electrojet_upper_lower_index_one_miniut_all_years.csv")
SUPERMAG_IMFB_FILEPATH = (SUPERMAG_DATA_DIR / "supermag_imf_b_gsm_one_minute_all_years.csv")
SUPERMAG_DESCRIBE_FILEPATH = SUPERMAG_DATA_DIR / "describe_stats.csv"
NEGATIVE_SML_DERIVATIVES_FP = SUPERMAG_DATA_DIR / "negative_sml_derivatives.json"

# medians
AL_MEDIAN = -50  # reference
AL_DERIVATIVES_MEDIAN = -4  # 1 minute

DESCRIBE_STATS = pd.read_csv(SUPERMAG_DESCRIBE_FILEPATH, index_col=0)
SML_MEDIAN = DESCRIBE_STATS["SML"]["50%"]
with open(NEGATIVE_SML_DERIVATIVES_FP, "r") as f:
    loaded_data_json = json.load(f)
NEG_SML_DERIVATIVES_MEDIAN = loaded_data_json["neg_sml_derivatives_median"]
