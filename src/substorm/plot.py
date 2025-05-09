# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/15
@DESCRIPTION: plot functions
"""
import os.path
from typing import Optional

import pandas as pd
from matplotlib import pyplot as plt


def plot(
    time: pd.Series,
    imf_bz: pd.Series,
    ae: pd.Series,
    al: pd.Series,
    au: pd.Series,
    phases: pd.DataFrame,
    if_show: bool = False,
    if_save: bool = False,
    sdir: str = "./figs",
) -> Optional[plt.figure]:
    """
    show and return a fig.
    @param if_save: if save, set 'True'
    @param if_show: if show, set 'True'
    @param sdir: the dir where the fig will be saved
    @param phases: index is datetime type, and the columns include "recovery_phase_start", "recovery_phase_end", "expansion_phase_start", "expansion_phase_end", "growth_phase_start", "growth_phase_end"
    @param time: x data
    @param imf_bz: IMF_Bz
    @param ae: AE
    @param al: AL
    @param au: AU
    @return:
    """
    assert (
        len(time) == len(imf_bz) == len(ae) == len(al) == len(au)
    ), "Series must all have the same length."
    series_ls = [imf_bz, ae, al, au]
    reference_index = series_ls[0].index
    all_same = all(series.index.equals(reference_index) for series in series_ls)
    assert all_same, "imf_bz, ae, al, au must have the same index."
    assert list(phases.columns) == [
        "growth_phase_start",
        "growth_phase_end",
        "expansion_phase_start",
        "expansion_phase_end",
        "recovery_phase_start",
        "recovery_phase_end",
    ], "DataFrame columns do not match the expected list (order-independent)."
    if not os.path.exists(sdir):
        os.mkdir(sdir)
    # plot
    fig = plt.figure(figsize=(4 * 10, 3 * 10))
    plt.plot(time, ae, label="AE", color="green")
    plt.plot(time, au, label="AU", color="red")
    plt.plot(time, al, label="AL", color="blue")
    plt.plot(time, 10 * imf_bz, label="10x IMF_Bz", color="black")
    # phases
    growth_phase = phases[["growth_phase_start", "growth_phase_end"]]
    expansion_phase = phases[["expansion_phase_start", "expansion_phase_end"]]
    recovery_phase = phases[["recovery_phase_start", "recovery_phase_end"]]
    # add phases info to the fig
    for _, row in expansion_phase.iterrows():
        if (row["expansion_phase_start"] is pd.NaT) or (
            row["expansion_phase_end"] is pd.NaT
        ):
            continue
        plt.axvspan(
            row["expansion_phase_start"],
            row["expansion_phase_end"],
            color="red",
            alpha=0.2,
        )
    for _, row in recovery_phase.iterrows():
        if (row["recovery_phase_start"] is pd.NaT) or (
            row["recovery_phase_end"] is pd.NaT
        ):
            continue
        plt.axvspan(
            row["recovery_phase_start"],
            row["recovery_phase_end"],
            color="blue",
            alpha=0.2,
        )
    for _, row in growth_phase.iterrows():
        if (row["growth_phase_end"] is pd.NaT) or (row["growth_phase_end"] is pd.NaT):
            continue
        plt.axvspan(
            row["growth_phase_start"], row["growth_phase_end"], color="green", alpha=0.2
        )
    # add label, title, legend etc.
    ax = plt.gca()  # get the current axis
    # todo:: customize xlabel
    plt.ylabel("unit: nT")
    plt.title("substorm phases")
    plt.legend(loc="lower left")
    # show vertical grid
    ax.grid(
        True, which="major", axis="x", linestyle=":", color="black", alpha=0.7
    )  # 设置 x 轴网格线
    ax.grid(
        True, which="major", axis="y", linestyle="--", color="gray", alpha=0.7
    )  # 设置 y 轴网格线
    if if_show:
        plt.show()
    if if_save:
        plt.savefig(os.path.join(sdir, "substorm.png"))
    plt.close()
    return fig
