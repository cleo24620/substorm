from pathlib import Path

import pandas as pd

import config
from substorm.determine import SubstormDetermine


def main():
    filepath = Path(config.OMNI_DAY_DIR) / '1995-01-01.csv'
    df = pd.read_csv(filepath, index_col=0)
    df.index = pd.to_datetime(df.index)
    substorm = SubstormDetermine(timestamps=df.index.values, imf_bz=df['IMF_GSM_Bz'],
                                 lower_electrojet_index=df['AL'], lower_electrojet_index_median=config.AL_MEDIAN,
                                 lower_electrojet_index_derivatives_median=config.AL_DERIVATIVES_MEDIAN)
    print("Substorm expansion phase:")
    print(substorm.expansion_phase)
    print("\nSubstorm recovery phase:")
    print(substorm.recovery_phase)
    print("\nSubstorm growth phase:")
    print(substorm.growth_phase)


if __name__ == '__main__':
    main()
