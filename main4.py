# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/16
@DESCRIPTION: get all the substorm phases info files as .asc and .pkl type.
"""
import os
import time

import pandas as pd

from substorm import product
from substorm.determine import SubStorm, get_fn_time

dir = r"D:\cleo\master\substorm\data\pkl020"
fns = os.listdir(dir)
sdir_asc = r"D:\cleo\master\substorm\data\asc030"
if not os.path.exists(sdir_asc):
    os.mkdir(sdir_asc)
sdir_pkl = r"D:\cleo\master\substorm\data\pkl030"
if not os.path.exists(sdir_pkl):
    os.mkdir(sdir_pkl)
for fn in fns:
    fn_t = get_fn_time(fn)
    sfn_asc = f"hro1_omni_{fn_t}_030.asc"
    sfn_pkl = f"hro1_omni_{fn_t}_030.pkl"
    sfp_asc = os.path.join(sdir_asc, sfn_asc)
    sfp_pkl = os.path.join(sdir_pkl, sfn_pkl)
    asc_save = True
    pkl_save = True
    if os.path.isfile(sfp_asc):
        print(f"{sfn_asc} already exists.")
        asc_save = False
    if os.path.isfile(sfp_pkl):
        print(f"{sfn_pkl} already exists.")
        pkl_save = False
    if not asc_save and not pkl_save:
        continue
    st = time.time()
    fp = os.path.join(dir, fn)
    data = pd.read_pickle(fp)
    substorm = SubStorm(data['IMF_Bz'], data['AL'], None, None)
    expansion, recovery, growth = substorm.priority_and_precede_follow_filter()
    et = time.time()
    print(f"get the phases info, cost {et - st}s.")
    if asc_save:
        substorm.determine.save_list(expansion, recovery, growth, sdir_asc, sfn_asc, stype='asc')
    if pkl_save:
        substorm.determine.save_list(expansion, recovery, growth, sdir_pkl, sfn_pkl, stype='pkl')
