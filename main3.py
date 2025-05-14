# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/16
@DESCRIPTION: choose one pkl020 file to analyze phases of substorm
"""
# %%
import pandas as pd

from substorm.determine import SubStorm

# %%
fp = "data/pkl020/hro1_omni_200409_020.pkl"
data = pd.read_pickle(fp)

from config import AL_MEDIAN, AL_DERIVATIVES_MEDIAN

substorm = SubStorm(data['IMF_Bz'], data['AL'], lower_electrojet_index_median=AL_MEDIAN,
                    lower_electrojet_index_diff_time_median=AL_DERIVATIVES_MEDIAN)

expansion, recovery, growth = substorm.priority_and_precede_follow_filter()

print("expansion:\n", expansion.iloc[:10, :], "\n")
print("recovery:\n", recovery.iloc[:10, :], "\n")
print("growth:\n", growth.iloc[:10, :], "\n")
