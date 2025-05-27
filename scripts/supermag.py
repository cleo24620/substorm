import pandas as pd

import config
from substorm import determine

# Save substorm list files
file_format = '.csv'
for fp in config.SUPERMAG_DAY_DIR.iterdir():
    df = pd.read_csv(fp, index_col=0)
    df.index = pd.to_datetime(df.index)
    try:
        substorm_determine = determine.SubstormDetermine(timestamps=df.index.values, imf_bz=df['GSM_Bz'],
                                                         lower_electrojet_index=df['SML'],
                                                         lower_electrojet_index_median=config.SML_MEDIAN,
                                                         lower_electrojet_index_derivatives_median=config.NEG_SML_DERIVATIVES_MEDIAN,
                                                         nan_ratio_threshold=config.MAX_NAN_RATIO)
    except Exception as e:
        print(f"Error: {e}")
    if (substorm_determine.expansion_phase is None) and (substorm_determine.growth_phase is None) and (
            substorm_determine.recovery_phase is None):
        continue
    sfn = fp.stem + file_format
    sfp = config.SUPERMAG_SUBSTORM_LIST_DIR / sfn
    if not sfp.exists():
        determine.save_list(expansion_phase=substorm_determine.expansion_phase,
                            recovery_phase=substorm_determine.recovery_phase,
                            growth_phase=substorm_determine.growth_phase, sdir=config.SUPERMAG_SUBSTORM_LIST_DIR,
                            sfn=sfn,
                            stype=
                            file_format)
