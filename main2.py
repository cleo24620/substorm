# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/16
@DIR_PATH: ./
@DESCRIPTION: preprocess all the original files into pre-data files (pay attention that not every file have corresponding pre-data file).
"""
import os

from substorm import short_funcs, data

# %%
dir = r"Z:\aw\substorm\OMNIData"  # the dir where the original files saved
fns = os.listdir(dir)  # pay attention the dir just save the original files, not include other files.
sdir = "./data/pkl010"  # dir where the 010 version files saved
for fn in fns:
    fp = os.path.join(dir, fn)
    sfn = f"hro1_omni_{short_funcs.get_fn_time(fn)}_010.pkl"
    data.get_pkl010(fp, sdir, sfn)

# %% pkl020
dir = sdir
fns = os.listdir(dir)
sdir = "./data/pkl020"
for fn in fns:
    fp = os.path.join(dir, fn)
    data.get_pkl020(fp, sdir)
