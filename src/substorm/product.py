# -*- coding: utf-8 -*-
"""
@Author      : cleo
@Date        : 2024/10/8 21:49
"""
import os
import time

import pandas as pd


def save_list(
    expansion_phase: pd.DataFrame,
    recovery_phase: pd.DataFrame,
    growth_phase: pd.DataFrame,
    sdir: str,
    sfn: str,
    stype: str,
) -> None:
    """

    @param expansion_phase:
    @param recovery_phase:
    @param growth_phase:
    @param sdir:
    @param sfn:
    @param stype: the type of the file to save
    @return:
    """
    if expansion_phase.empty:
        print("the expansion phase is empty")
        return None
    st = time.time()
    # 创建一个空列表用于存储结果
    results = []
    for _, exp_row in expansion_phase.iterrows():
        condition1 = recovery_phase["start"] == exp_row["end"]
        condition2 = growth_phase["end"] == exp_row["start"]
        recovery_match = recovery_phase[condition1]
        growth_match = growth_phase[condition2]
        if recovery_match.empty and growth_match.empty:
            results.append(
                {
                    "growth_phase_start": pd.NaT,
                    "growth_phase_end": pd.NaT,
                    "expansion_phase_start": exp_row["start"],
                    "expansion_phase_end": exp_row["end"],
                    "recovery_phase_start": pd.NaT,
                    "recovery_phase_end": pd.NaT,
                }
            )
        elif recovery_match.empty and not growth_match.empty:
            results.append(
                {
                    "growth_phase_start": growth_match.iloc[0, 0],
                    "growth_phase_end": growth_match.iloc[0, 1],
                    "expansion_phase_start": exp_row["start"],
                    "expansion_phase_end": exp_row["end"],
                    "recovery_phase_start": pd.NaT,
                    "recovery_phase_end": pd.NaT,
                }
            )
        elif not recovery_match.empty and growth_match.empty:
            results.append(
                {
                    "growth_phase_start": pd.NaT,
                    "growth_phase_end": pd.NaT,
                    "expansion_phase_start": exp_row["start"],
                    "expansion_phase_end": exp_row["end"],
                    "recovery_phase_start": recovery_match.iloc[0, 0],
                    "recovery_phase_end": recovery_match.iloc[0, 1],
                }
            )
        else:
            results.append(
                {
                    "growth_phase_start": growth_match.iloc[0, 0],
                    "growth_phase_end": growth_match.iloc[0, 1],
                    "expansion_phase_start": exp_row["start"],
                    "expansion_phase_end": exp_row["end"],
                    "recovery_phase_start": recovery_match.iloc[0, 0],
                    "recovery_phase_end": recovery_match.iloc[0, 1],
                }
            )
    result_df = pd.DataFrame(results)
    sfp = os.path.join(sdir, sfn)
    if stype == "pkl":
        result_df.to_pickle(sfp)
        print(f"saved {sfn}")
    if stype == "asc":
        result_df.to_csv(sfp)
        print(f"saved {sfn}")
    et = time.time()
    print(f"the {sfn} write took {et - st}")
    return None
