# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/16
@DESCRIPTION: plot 1 month substorm figure
"""
import pandas as pd

from substorm import plot

fp_pkl020 = r"D:\cleo\master\substorm\data\pkl020\hro1_omni_199502_020.pkl"
fp_phases = r"D:\cleo\master\substorm\data\pkl030\hro1_omni_199502_030.pkl"
data = pd.read_pickle(fp_pkl020)
phases = pd.read_pickle(fp_phases)
time = data.index
plot(time, data['IMF_Bz'], data['AE'], data['AL'], data['AU'], phases, if_save=True)
