"""
Time resolution: 1 minute;
Time resolution of derivatives: 1 minute;
"""

import json
from pathlib import Path

import pandas as pd

# crawler
OMNI_HRO_MODIFIED_URL_Y = "https://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/modified/"  # url of the year file
OMNI_HRO_MODIFIED_URL_M = "https://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/modified/monthly_1min/"  # url of the month file
HTML_TAG_M = "a"
HREF_REGEX_PATTERN_M = r"^omni_min(\d{4})(0[1-9]|1[0-2])\.asc$"  # regular expression pattern
PROXIES = {'http': 'http://127.0.0.1:7890',
           'https': 'http://127.0.0.1:7890'
           }

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
OMNI_DAY_DIR = OMNI_DATA_DIR / 'days'
OMNI_DAY_PREFIX = ''
OMNI_DAY_EXTENSION = 'csv'
OMNI_START_YEAR = 1995
OMNI_START_MONTH = 1
OMNI_START_DAY = 1
OMNI_END_YEAR = 2025
OMNI_END_MONTH = 3
OMNI_END_DAY = 31
OMNI_SUBSTORM_LIST_DIR = OMNI_DATA_DIR / 'substorm_list'
SUPERMAG_DATA_DIR = Path("./data/supermag")
SME_FILEPATH = SUPERMAG_DATA_DIR / "supermag_electrojet_index_one_miniut_all_years.csv"
SMU_SML_FILEPATH = (SUPERMAG_DATA_DIR / "supermag_electrojet_upper_lower_index_one_miniut_all_years.csv")
SUPERMAG_IMFB_FILEPATH = (SUPERMAG_DATA_DIR / "supermag_imf_b_gsm_one_minute_all_years.csv")
SUPERMAG_DESCRIBE_FILEPATH = SUPERMAG_DATA_DIR / "describe_stats.csv"
NEGATIVE_SML_DERIVATIVES_FP = SUPERMAG_DATA_DIR / "negative_sml_derivatives.json"
SUPERMAG_DAY_DIR = SUPERMAG_DATA_DIR / 'days'
SUPERMAG_SUBSTORM_LIST_DIR = SUPERMAG_DATA_DIR / 'substorm_list'

# medians
AL_MEDIAN = -50  # reference
AL_DERIVATIVES_MEDIAN = -4  # 1 minute

DESCRIBE_STATS = pd.read_csv(SUPERMAG_DESCRIBE_FILEPATH, index_col=0)
SML_MEDIAN = DESCRIBE_STATS["SML"]["50%"]
with open(NEGATIVE_SML_DERIVATIVES_FP, "r") as f:
    loaded_data_json = json.load(f)
NEG_SML_DERIVATIVES_MEDIAN = loaded_data_json["neg_sml_derivatives_median"]

# Substorm column names
SUBSTORM_COLUMN_NAMES = ['growth_phase_start',
                         'growth_phase_end',
                         'expansion_phase_start',
                         'expansion_phase_end',
                         'recovery_phase_start',
                         'recovery_phase_end'
                         ]

SUBSTORM_PHASE_DURATION_NAMES = ['growth_duration',
                                 'expansion_duration',
                                 'recovery_duration', ]
SUBSTORM_DURATION_NAME = 'substorm_duration'
OMNI_SUBSTORM_DURATION_DIR = OMNI_DATA_DIR / 'substorm_duration'
SUPERMAG_SUBSTORM_DURATION_DIR = SUPERMAG_DATA_DIR / 'substorm_duration'
OMNI_SUBSTORM_LIST_STATS_DIR = OMNI_DATA_DIR / 'substorm_list_statistics'
SUPERMAG_SUBSTORM_LIST_STATS_DIR = SUPERMAG_DATA_DIR / 'substorm_list_statistics'
DURATIONS_AVERAGE_NAMES = ['growth_durations', 'expansion_durations', 'recovery_durations', 'substorm_durations',
                           ]
RATIOS_AVERAGE_NAME = 'substorm_duration_ratios'
OMNI_STATS_AVERAGE_FP = OMNI_DATA_DIR / 'substorm_stats_average.json'
SUPERMAG_STATS_AVERAGE_FP = SUPERMAG_DATA_DIR / 'substorm_stats_average.json'
