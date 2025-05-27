import re
import time
from pathlib import Path

import pandas as pd
from numpy.typing import NDArray
from pandas import DataFrame

import config


def get_fn_time(fn: str) -> str:
    """
    get time from filename
    @param fn: the filename
    @return:
    """
    match = re.search(r"\d{6}", fn)
    return match.group(0)


def get_intervals(data: pd.Series, cond: bool) -> pd.Series:
    """
    Based on the given conditions, identify the growth, expansion, recovery phase intervals from the data.
    @param data: original data
    @param cond: condition
    @return:
    """
    filtered_dates = data[cond]
    gaps = (
            filtered_dates.index.to_series().diff() > pd.Timedelta(minutes=1)
    ).cumsum()  # default time_resolution is 1 min.
    intervals = filtered_dates.groupby(gaps).apply(
        lambda x: (x.index[0], x.index[-1])
    )
    return intervals


def merge_intervals(intervals: pd.Series) -> pd.DataFrame:
    """
    if the time diff between two intervals is less than 12.5 minutes, merge them.
    @param intervals:
    @return:
    """
    merged_intervals = []
    # from the 1st interval
    current_start, current_end = intervals.iloc[0][0], intervals.iloc[0][1]
    for i in range(1, len(intervals)):
        next_start, next_end = intervals.iloc[i][0], intervals.iloc[i][1]
        # check that the time interval between adjacent intervals is less than 12.5 minutes.
        if (next_start - current_end) <= pd.Timedelta(minutes=12.5):
            # if the time interval is less than 12.5 minutes, merge the adjacent intervals.
            current_end = next_end
        else:
            # if the time interval is larger than 12.5 minutes, add the current interval into merged_intervals.
            merged_intervals.append((current_start, current_end))
            # update
            current_start, current_end = next_start, next_end
    # add the last interval into merged_intervals
    merged_intervals.append((current_start, current_end))
    merged_intervals_df = pd.DataFrame(merged_intervals, columns=["start", "end"])
    return merged_intervals_df


def remove_1m_interval(intervals: pd.DataFrame) -> pd.DataFrame:
    """
    if the interval less than 1 minute, remove it.
    @param intervals: DataFrame with 2 columns: ['start', 'end']
    @return: the same type as intervals
    """
    return intervals[intervals["start"] != intervals["end"]]


def apply_priority_to_phases_intervals(
        high_priority_intervals: pd.DataFrame, low_priority_intervals: pd.DataFrame
) -> pd.DataFrame:
    """
    use the priority to trim the low_priority_intervals.
    @param high_priority_intervals:
    @param low_priority_intervals:
    @return:
    """
    # initialize a new DataFrame for saving the trimmed low_priority_intervals.
    adjusted_low_priority_intervals = []
    for i, low_interval in low_priority_intervals.iterrows():
        low_interval_st = low_interval["start"]
        low_interval_et = low_interval["end"]
        for _, high_interval in high_priority_intervals.iterrows():
            high_interval_st = high_interval["start"]
            high_interval_et = high_interval["end"]
            # check overlap
            if (
                    low_interval_st < high_interval_et
                    and low_interval_et > high_interval_st
            ):
                # overlapping section: trim the low_interval
                if (
                        low_interval_st >= high_interval_st
                        and low_interval_et <= high_interval_et
                ):
                    # if the entire low_interval is overlapped by high_interval, remove the low_interval
                    low_interval_st = low_interval_et = None
                    break
                elif (
                        low_interval_st < high_interval_st
                        and low_interval_et > high_interval_et
                ):
                    # if the entire high_interval is overlapped by low_interval, divide the low_interval into 2 parts.
                    adjusted_low_priority_intervals.append(
                        {"start": low_interval_st, "end": high_interval_st}
                    )
                    low_interval_st = high_interval_et
                elif low_interval_st < high_interval_st:
                    # 如果 recovery 的前半段不重叠，保留前半段
                    adjusted_low_priority_intervals.append(
                        {"start": low_interval_st, "end": high_interval_st}
                    )
                    low_interval_st = high_interval_et
                elif low_interval_et > high_interval_et:
                    # 如果 recovery 的后半段不重叠，保留后半段
                    low_interval_st = high_interval_et
        # 如果重叠的调整后依旧有剩余部分
        if (
                low_interval_st is not None
                and low_interval_et is not None
                and low_interval_st < low_interval_et
        ):
            adjusted_low_priority_intervals.append(
                {"start": low_interval_st, "end": low_interval_et}
            )
    adjusted_low_priority_intervals_df = pd.DataFrame(adjusted_low_priority_intervals, columns=["start", "end"])
    return adjusted_low_priority_intervals_df


class SubstormDetermine:
    """
    identification of substorms
    """

    def __init__(
            self,
            timestamps: NDArray,
            imf_bz: pd.Series,
            lower_electrojet_index: pd.Series,
            lower_electrojet_index_median: float,
            lower_electrojet_index_derivatives_median: float,
            nan_ratio_threshold: float = config.MAX_NAN_RATIO,
    ):
        assert timestamps.size == imf_bz.size == lower_electrojet_index.size
        self.timestamps = timestamps
        self.imf_bz = imf_bz
        self.lower_electrojet_index = lower_electrojet_index
        self.median = lower_electrojet_index_median
        self.lower_electrojet_index_derivatives_median = lower_electrojet_index_derivatives_median
        self.nan_ratio_threshold = nan_ratio_threshold

        self.expansion_phase, self.recovery_phase, self.growth_phase = None, None, None
        if self.check_nan_ratio():
            self.lower_electrojet_index_derivatives = self.lower_electrojet_index.diff()
            # Get the final result.
            self.expansion_phase, self.recovery_phase, self.growth_phase = self.priority_and_precede_follow_filter()

    def check_nan_ratio(self):
        # interplanetary magnetic field z component
        imfbz_nan_count = self.imf_bz.isna().sum()
        lower_ele_index_nan_count = self.lower_electrojet_index.isna().sum()
        total_elements = self.imf_bz.size
        imfbz_nan_proportion = imfbz_nan_count / total_elements
        lower_ele_index_nan_proportion = lower_ele_index_nan_count / total_elements

        if imfbz_nan_proportion > self.nan_ratio_threshold:
            print(f"The NaN proportion of interplanetary magnetic field z component is {imfbz_nan_proportion:.2f}")
            print(f"It exceeds the set threshold {self.nan_ratio_threshold:.2f}.")
            print("The substorm phase determination will be skipped.")
            return False
        elif lower_ele_index_nan_proportion > self.nan_ratio_threshold:
            print(f"The NaN proportion of lower electrojet index is {lower_ele_index_nan_proportion:.2f}.")
            print(f"It exceeds the set threshold {self.nan_ratio_threshold:.2f}.")
            print("The substorm phase determination will be skipped.")
            return False
        else:
            return True

    def pre_expansion(self) -> pd.DataFrame | None:
        """
        get the pre-expansion intervals
        @return:
        """
        intervals_expansion1 = get_intervals(self.lower_electrojet_index_derivatives,
                                             self.lower_electrojet_index_derivatives < self.lower_electrojet_index_derivatives_median)

        # 对每个interval在原series中进行切片并获取最小值
        min_values = intervals_expansion1.apply(
            lambda x: self.lower_electrojet_index[x[0]: x[1]].min()
        )  # return pd.Series

        # 保留最小值小于 median 的区间 (2nd condition)
        intervals_expansion12 = intervals_expansion1[min_values < self.median]
        if len(intervals_expansion12) == 0:
            return None

        # merge
        merged_intervals_expansion = merge_intervals(intervals_expansion12)

        # trim
        trimmed_intervals_expansion = []
        for i in range(len(merged_intervals_expansion)):
            start = merged_intervals_expansion.iloc[i]["start"]
            end = merged_intervals_expansion.iloc[i]["end"]
            sliced_al = self.lower_electrojet_index[start:end]
            start_time = sliced_al.idxmax()
            end_time = sliced_al.idxmin()
            if start_time > end_time:
                continue
            # 修剪后的 interval 以最大值开始，最小值结束
            trimmed_intervals_expansion.append((start_time, end_time))
        trimmed_intervals_expansion_df = pd.DataFrame(
            trimmed_intervals_expansion, columns=["start", "end"]
        )

        # remove 1 minute interval
        remove_1m_intervals_expansion = remove_1m_interval(
            trimmed_intervals_expansion_df
        )

        return remove_1m_intervals_expansion

    def pre_recovery(self) -> pd.DataFrame | None:
        """
        get pre-recovery intervals
        @param self.AL:
        @return:
        """
        # Based on the given condition, get the intervals from data.
        al_series = pd.Series(self.lower_electrojet_index, index=self.timestamps)
        intervals_recovery = get_intervals(self.lower_electrojet_index, self.lower_electrojet_index < self.median)
        if len(intervals_recovery) == 0:
            return None

        # merge
        merged_intervals_recovery = merge_intervals(intervals_recovery)

        # remove
        remove_1m_intervals_recovery = remove_1m_interval(merged_intervals_recovery)

        return remove_1m_intervals_recovery

    def pre_growth(self) -> pd.DataFrame | None:
        # Based on the given condition, get the intervals from data.
        intervals_growth = get_intervals(self.imf_bz, self.imf_bz < 0)
        if len(intervals_growth) == 0:
            return None

        # merge
        merged_intervals_growth = merge_intervals(intervals_growth)

        # remove
        remove_1m_intervals_growth = remove_1m_interval(merged_intervals_growth)

        return remove_1m_intervals_growth

    def priority_and_precede_follow_filter(
            self,
    ) -> (
            tuple[None, None, None]
            | tuple[DataFrame, None, None]
            | tuple[DataFrame, DataFrame, None]
            | tuple[DataFrame, DataFrame, DataFrame]
    ):
        """
        Use the priority and precede follow filter to get the final intervals.
        @return:
        """
        # Column names
        column_names = ['start', 'end']
        # if some intervals are None
        remove_1m_intervals_expansion = self.pre_expansion()
        if remove_1m_intervals_expansion is None:
            return pd.DataFrame(columns=column_names), pd.DataFrame(columns=column_names), pd.DataFrame(
                columns=column_names)
        remove_1m_intervals_recovery = self.pre_recovery()
        if remove_1m_intervals_recovery is None:
            return remove_1m_intervals_expansion.reset_index(drop=True), pd.DataFrame(
                columns=column_names), pd.DataFrame(columns=column_names)
        remove_1m_intervals_growth = self.pre_growth()
        if remove_1m_intervals_growth is None:
            return remove_1m_intervals_expansion.reset_index(drop=True), remove_1m_intervals_recovery.reset_index(
                drop=True), pd.DataFrame(columns=column_names)

        # priority: expansion and recovery
        adjusted_recovery_intervals = apply_priority_to_phases_intervals(
            remove_1m_intervals_expansion, remove_1m_intervals_recovery
        )
        # 筛选 recovery_intervals：recovery 的 start 必须是 expansion 的 end
        follow_recovery_intervals = adjusted_recovery_intervals[
            adjusted_recovery_intervals["start"].isin(
                remove_1m_intervals_expansion["end"]
            )
        ]
        # priority: expansion and growth
        adjusted_growth_intervals1 = apply_priority_to_phases_intervals(
            remove_1m_intervals_expansion, remove_1m_intervals_growth
        )
        adjusted_growth_intervals2 = apply_priority_to_phases_intervals(
            follow_recovery_intervals, adjusted_growth_intervals1
        )
        # 筛选 growth_intervals：growth 的 end 必须是 expansion 的 start
        precede_growth_intervals = adjusted_growth_intervals2[
            adjusted_growth_intervals2["end"].isin(
                remove_1m_intervals_expansion["start"]
            )
        ]

        return (
            remove_1m_intervals_expansion.reset_index(drop=True),
            follow_recovery_intervals.reset_index(drop=True),
            precede_growth_intervals.reset_index(drop=True),
        )


def save_list(
        expansion_phase: pd.DataFrame,
        recovery_phase: pd.DataFrame,
        growth_phase: pd.DataFrame,
        sdir: str,
        sfn: str,
        stype: str = 'asc',
):
    """

    @param expansion_phase:
    @param recovery_phase:
    @param growth_phase:
    @param sdir:
    @param sfn:
    @param stype: the type of the file to save
    @return:
    """
    sdir = Path(sdir)
    sdir.mkdir(parents=True, exist_ok=True)
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
    sfp = sdir / sfn
    if stype == ".pkl":
        result_df.to_pickle(sfp)
        print(f"saved {sfn}")
    if stype == '.csv':
        result_df.to_csv(sfp, index=False)
        print(f"saved {sfn}")
    et = time.time()
    print(f"the {sfn} write took {et - st}")
    return None
