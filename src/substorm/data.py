# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/16
@DESCRIPTION: prepare the data
"""

import os
from typing import List, Optional

import numpy as np
import pandas as pd

from substorm import config, short_funcs


def get_pkl010(fp: str, sdir: str, sfn: str, vars_=config.hro1_modified_vars,
               specify_vars=config.preprocess_omnidata_kwargs['specify_vars'],
               specify_vars_rename=config.preprocess_omnidata_kwargs['specify_vars_rename'], preview=False) -> None:
    """
    pkl010 is the file with rename and drop but without datetime and nan process.
    @param fp: file path of the original file
    @param sdir: dir path where the processed file saved
    @param sfn: filename of the processed file
    @param vars_: what vars the original file has
    @param specify_vars: what vars we want to keep
    @param specify_vars_rename: rename these keep vars
    @param preview: preview or not
    @return:
    """
    if preview:
        print(pd.read_csv(fp, sep='\s+', nrows=100, names=vars_))
    if not os.path.exists(sdir):
        os.mkdir(sdir)
    sfp = os.path.join(sdir, sfn)
    if os.path.isfile(sfp):
        print(f"{sfn} already exits.")
        return None
    # read the original data
    df = pd.read_csv(fp, sep='\s+', names=vars_)  # the original data sep is whitespace of different length
    df_specify = df[specify_vars]
    df_rename = df_specify.rename(columns=dict(zip(specify_vars, specify_vars_rename)))
    df_rename.to_pickle(sfp)
    print(f'saved {sfn}')
    assert df.shape[1] != df_rename.shape[1], "don't drop the specified vars"
    return None


def get_pkl020(fp: str, sdir: str = './data') -> Optional[List[pd.Series]]:
    """
    compared to the pkl010, the pkl020 process datetime and Nan.
    @param sdir: dir path where the processed file saved
    @param fp: the file path of the pkl010 file
    @return: IMF_Bz, AE, AL, AU
    """
    if not os.path.exists(sdir):
        os.mkdir(sdir)
    # determine whether the file exits
    fn_time = short_funcs.get_fn_time(fp)
    sfn_time = fn_time
    sfn = f"hro1_omni_{sfn_time}_020.pkl"
    sfp = os.path.join(sdir, sfn)
    if os.path.isfile(sfp):
        print(f"{sfn} already exits.")
        return None
    # read the data
    data = pd.read_pickle(fp)
    # get the datatime info and set it as the index column.
    # get month info for pd.to_datetime() because `the method expects minimally the following columns: "year", "month", "day" from official doc`
    data['Date'] = pd.to_datetime(data['Year'].astype(str) + data['Day'].astype(str), format='%Y%j')
    data['Datetime'] = data['Date'] + pd.to_timedelta(data['Hour'], unit='h') + pd.to_timedelta(data['Minute'],
                                                                                                unit='m')
    data = data.drop(columns=['Year', 'Day', 'Hour', 'Minute', 'Date'])
    # set index to datatime
    data = data.set_index('Datetime')
    # process filling value
    data['IMF_Bz'] = data['IMF_Bz'].replace(config.hro1_vars_fv['IMF_Bz'], np.nan)
    data['AE'] = data['AE'].replace(config.hro1_vars_fv['AE'], np.nan)
    data['AL'] = data['AL'].replace(config.hro1_vars_fv['AL'], np.nan)
    data['AU'] = data['AU'].replace(config.hro1_vars_fv['AU'], np.nan)
    cond1 = data['IMF_Bz'].isna().sum() > (0.1 * len(data['IMF_Bz']))
    cond2 = data['AE'].isna().sum() > (0.1 * len(data['AE']))
    cond3 = data['AL'].isna().sum() > (0.1 * len(data['AL']))
    cond4 = data['AU'].isna().sum() > (0.1 * len(data['AU']))
    if cond1:
        print("too many nans in IMF_Bz")
    if cond2:
        print("too many nans in AE")
    if cond3:
        print("too many nans in AL")
    if cond4:
        print("too many nans in AU")
    if cond1 or cond2 or cond3 or cond4:
        return None
    else:
        data[['IMF_Bz', 'AE', 'AL', 'AU']] = data[['IMF_Bz', 'AE', 'AL', 'AU']].interpolate()
    data.to_pickle(sfp)
    print(f'saved {sfn}')
    return None
