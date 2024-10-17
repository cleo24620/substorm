# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/15
@DIR_PATH: ./substorm
"""

hro_modified_url_y = "https://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/modified/"  # url of 1 year file
hro_modified_url_m = "https://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/modified/monthly_1min/"  # url of 1 month file
html_tag_m = html_tag_y = 'a'
href_pattern_m = r"omni_min\d{6}.asc"

hro1_modified_vars = ['Year', 'Day', 'Hour', 'Minute', 'ID for IMF spacecraft', 'ID for SW Plasma spacecraft',
                      '# of points in IMF averages', '# of points in Plasma averages', 'Percent interp',
                      'Timeshift, sec', 'RMS, Timeshift', 'RMS, Phase front normal', 'Time btwn observations, sec',
                      'Field magnitude average, nT', 'Bx, nT (GSE, GSM)', 'By, nT (GSE)', 'Bz, nT (GSE)',
                      'By, nT (GSM)', 'Bz, nT (GSM)', 'RMS SD B scalar, nT', 'RMS SD field vector, nT',
                      'Flow speed, km/s', 'Vx Velocity, km/s, GSE', 'Vy Velocity, km/s, GSE', 'Vz Velocity, km/s, GSE',
                      'Proton Density, n/cc', 'Temperature, K', 'Flow pressure, nPa', 'Electric field, mV/m',
                      'Plasma beta', 'Alfven mach number', 'X(s/c), GSE, Re', 'Y(s/c), GSE, Re', 'Z(s/c), GSE, Re',
                      'BSN location, Xgse, Re', 'BSN location, Ygse, Re', 'BSN location, Zgse, Re', 'AE-index, nT',
                      'AL-index, nT', 'AU-index, nT', 'SYM/D index, nT', 'SYM/H index, nT', 'ASY/D index, nT',
                      'ASY/H index, nT', 'PC(N) index', 'Na/Np Ratio',
                      'Magnetosonic mach number']  # vars of hro 1 minute modified version file

preprocess_omnidata_kwargs = {
    'specify_vars': ['Year', 'Day', 'Hour', 'Minute', 'Bz, nT (GSM)', 'AE-index, nT', 'AL-index, nT', 'AU-index, nT'],
    'specify_vars_rename': ['Year', 'Day', 'Hour', 'Minute', 'IMF_Bz', 'AE', 'AL', 'AU']}

hro1_vars_fv = {'IMF_Bz': 9999.99, 'AE': 99999, 'AL': 99999, 'AU': 99999}
