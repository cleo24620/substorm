# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/16
@DESCRIPTION: choose one pkl020 file to analyze phases of substorm
"""
# %%
import pandas as pd

from substorm.identification import SubStorm

# %%
fp = r"D:\cleo\master\substorm\data\pkl020\hro1_omni_200409_020.pkl"
data = pd.read_pickle(fp)
# %%
substorm = SubStorm(data['IMF_Bz'], data['AE'], data['AL'], data['AU'])

expansion, recovery, growth = substorm.priority_and_precede_follow_filter()

print("expansion:\n", expansion.iloc[:10, :], "\n")
print("recovery:\n", recovery.iloc[:10, :], "\n")
print("growth:\n", growth.iloc[:10, :], "\n")
