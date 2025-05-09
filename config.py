# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/15
@DIR_PATH: ./substorm
"""

HRO_MODIFIED_URL_Y = "https://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/modified/"  # url of 1 year file
HRO_MODIFIED_URL_M = "https://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/modified/monthly_1min/"  # url of 1 month file
HTML_TAG_M = "a"
HREF_PATTERN_M = r"omni_min\d{6}.asc"

HRO1_MODIFIED_VARS = [
    "Year",
    "Day",
    "Hour",
    "Minute",
    "ID for IMF spacecraft",
    "ID for SW Plasma spacecraft",
    "# of points in IMF averages",
    "# of points in Plasma averages",
    "Percent interp",
    "Timeshift, sec",
    "RMS, Timeshift",
    "RMS, Phase front normal",
    "Time btwn observations, sec",
    "Field magnitude average, nT",
    "Bx, nT (GSE, GSM)",
    "By, nT (GSE)",
    "Bz, nT (GSE)",
    "By, nT (GSM)",
    "Bz, nT (GSM)",
    "RMS SD B scalar, nT",
    "RMS SD field vector, nT",
    "Flow speed, km/s",
    "Vx Velocity, km/s, GSE",
    "Vy Velocity, km/s, GSE",
    "Vz Velocity, km/s, GSE",
    "Proton Density, n/cc",
    "Temperature, K",
    "Flow pressure, nPa",
    "Electric field, mV/m",
    "Plasma beta",
    "Alfven mach number",
    "X(s/c), GSE, Re",
    "Y(s/c), GSE, Re",
    "Z(s/c), GSE, Re",
    "BSN location, Xgse, Re",
    "BSN location, Ygse, Re",
    "BSN location, Zgse, Re",
    "AE-index, nT",
    "AL-index, nT",
    "AU-index, nT",
    "SYM/D index, nT",
    "SYM/H index, nT",
    "ASY/D index, nT",
    "ASY/H index, nT",
    "PC(N) index",
    "Na/Np Ratio",
    "Magnetosonic mach number",
]  # vars of hro 1 minute modified version file

PREPROCESS_OMNIDATA_KWARGS = {
    "specify_vars": [
        "Year",
        "Day",
        "Hour",
        "Minute",
        "Bz, nT (GSM)",
        "AE-index, nT",
        "AL-index, nT",
        "AU-index, nT",
    ],
    "specify_vars_rename": [
        "Year",
        "Day",
        "Hour",
        "Minute",
        "IMF_Bz",
        "AE",
        "AL",
        "AU",
    ],
}

HRO1_VARS_FV = {"IMF_Bz": 9999.99, "AE": 99999, "AL": 99999, "AU": 99999}

SUPERMAG_ELECTROJET_LOWER_INDEX_FILL_VALUE = 999999
SUPERMAG_ELECTROJET_UPPER_INDEX_FILL_VALUE = 999999