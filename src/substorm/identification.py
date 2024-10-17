# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/15
@DESCRIPTION: identification of substorms
"""

from typing import Optional

import pandas as pd
from pandas import DataFrame


def get_intervals(data: pd.Series, cond: bool) -> pd.Series:
    """
    give the condition, get the filtered intervals.
    @param data: original data
    @param cond: condition
    @return:
    """
    filtered_dates = data[cond]
    gaps = (filtered_dates.index.to_series().diff() > pd.Timedelta(
        minutes=1)).cumsum()  # default time_resolution is 1 min.
    intervals = filtered_dates.groupby(gaps).apply(lambda x: (x.index[0], x.index[-1]))  # todo: apply?
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
    merged_intervals_df = pd.DataFrame(merged_intervals, columns=['start', 'end'])
    return merged_intervals_df


def remove_1m_interval(intervals: pd.DataFrame) -> pd.DataFrame:
    """
    if the interval less than 1 minute, remove it.
    @param intervals: DataFrame with 2 columns: ['start', 'end']
    @return: the same type as intervals
    """
    return intervals[intervals['start'] != intervals['end']]


def apply_priority_to_phases_intervals(high_priority_intervals: pd.DataFrame,
                                       low_priority_intervals: pd.DataFrame) -> pd.DataFrame:
    """
    use the priority to trim the low_priority_intervals.
    @param high_priority_intervals:
    @param low_priority_intervals:
    @return:
    """
    # initialize a new DataFrame for saving the trimmed low_priority_intervals.
    adjusted_low_priority_intervals = []
    for i, low_interval in low_priority_intervals.iterrows():
        low_interval_st = low_interval['start']
        low_interval_et = low_interval['end']
        for _, high_interval in high_priority_intervals.iterrows():
            high_interval_st = high_interval['start']
            high_interval_et = high_interval['end']
            # check overlap
            if low_interval_st < high_interval_et and low_interval_et > high_interval_st:
                # overlapping section: trim the low_interval
                if low_interval_st >= high_interval_st and low_interval_et <= high_interval_et:
                    # if the entire low_interval is overlapped by high_interval, remove the low_interval
                    low_interval_st = low_interval_et = None
                    break
                elif low_interval_st < high_interval_st and low_interval_et > high_interval_et:
                    # if the entire high_interval is overlapped by low_interval, divide the low_interval into 2 parts.
                    adjusted_low_priority_intervals.append({'start': low_interval_st, 'end': high_interval_st})
                    low_interval_st = high_interval_et
                elif low_interval_st < high_interval_st:
                    # 如果 recovery 的前半段不重叠，保留前半段
                    adjusted_low_priority_intervals.append({'start': low_interval_st, 'end': high_interval_st})
                    low_interval_st = high_interval_et
                elif low_interval_et > high_interval_et:
                    # 如果 recovery 的后半段不重叠，保留后半段
                    low_interval_st = high_interval_et
        # 如果重叠的调整后依旧有剩余部分
        if low_interval_st is not None and low_interval_et is not None and low_interval_st < low_interval_et:
            adjusted_low_priority_intervals.append({'start': low_interval_st, 'end': low_interval_et})
    adjusted_low_priority_intervals_df = pd.DataFrame(adjusted_low_priority_intervals)
    return adjusted_low_priority_intervals_df


class SubStorm:
    """
    identification of substorms
    """

    def __init__(self, imf_bz: pd.Series, ae: pd.Series, al: pd.Series, au: pd.Series) -> None:
        # make sure that IMF_Bz, AE, AL, AU have the same time points.
        series_ls = [imf_bz, ae, al, au]
        reference_index = series_ls[0].index
        all_same = all(series.index.equals(reference_index) for series in series_ls)
        if all_same:
            print("All Series have the same index.")
        else:
            print("Not all Series have the same index.")
            raise ValueError("The series have different index.")
        self.imf_bz = imf_bz
        self.ae = ae
        self.al = al
        self.au = au

    def pre_expansion(self) -> Optional[pd.DataFrame]:
        """
        get the pre-expansion intervals
        @return:
        """
        AL_diff = self.al.diff()
        intervals_expansion1 = get_intervals(AL_diff, AL_diff < -4)
        # 对每个interval在原series中进行切片并获取最小值
        min_values = intervals_expansion1.apply(lambda x: self.al[x[0]:x[1]].min())
        # 保留最小值小于 -50 的区间
        intervals_expansion12 = intervals_expansion1[min_values < -50]
        # todo:: deal with return None problem (for now, use the pkl020 file, i don't encounter this problem)
        if len(intervals_expansion12) == 0:
            return None
        merged_intervals_expansion = merge_intervals(intervals_expansion12)
        # trim
        trimmed_intervals_expansion = []
        for i in range(len(merged_intervals_expansion)):
            start = merged_intervals_expansion.iloc[i]['start']
            end = merged_intervals_expansion.iloc[i]['end']
            # 对 AL 进行切片
            sliced_AL = self.al[start:end]
            # 找到最小值和最大值及其对应的时间点
            start_time = sliced_AL.idxmax()  # 最大值对应的时间点
            end_time = sliced_AL.idxmin()  # 最小值对应的时间点
            if start_time > end_time:
                continue
            # 修剪后的 interval 以最大值开始，最小值结束
            trimmed_intervals_expansion.append((start_time, end_time))
        trimmed_intervals_expansion_df = pd.DataFrame(trimmed_intervals_expansion, columns=['start', 'end'])
        remove_1m_intervals_expansion = remove_1m_interval(trimmed_intervals_expansion_df)
        return remove_1m_intervals_expansion

    def pre_recovery(self) -> Optional[pd.DataFrame]:
        """
        get pre-recovery intervals
        @param self.AL:
        @return:
        """
        intervals_recovery = get_intervals(self.al, self.al < -50)
        if len(intervals_recovery) == 0:
            return None
        merged_intervals_recovery = merge_intervals(intervals_recovery)
        remove_1m_intervals_recovery = remove_1m_interval(merged_intervals_recovery)
        return remove_1m_intervals_recovery

    def pre_growth(self) -> Optional[pd.DataFrame]:
        intervals_growth = get_intervals(self.imf_bz, self.imf_bz < 0)
        if len(intervals_growth) == 0:
            return None
        merged_intervals_growth = merge_intervals(intervals_growth)
        remove_1m_intervals_growth = remove_1m_interval(merged_intervals_growth)
        return remove_1m_intervals_growth

    def priority_and_precede_follow_filter(self) -> tuple[None, None, None] | tuple[DataFrame, None, None] | tuple[
        DataFrame, DataFrame, None] | tuple[DataFrame, DataFrame, DataFrame]:
        """
        use the priority and precede follow filter to get the final intervals.
        @return:
        """
        remove_1m_intervals_expansion = self.pre_expansion()
        if remove_1m_intervals_expansion is None:
            return None, None, None
        remove_1m_intervals_recovery = self.pre_recovery()
        if remove_1m_intervals_recovery is None:
            return remove_1m_intervals_expansion, None, None
        remove_1m_intervals_growth = self.pre_growth()
        if remove_1m_intervals_growth is None:
            return remove_1m_intervals_expansion, remove_1m_intervals_recovery, None
        adjusted_recovery_intervals = apply_priority_to_phases_intervals(remove_1m_intervals_expansion,
                                                                         remove_1m_intervals_recovery)
        # 1. 筛选 recovery_intervals：recovery 的 start 必须是 expansion 的 end
        follow_recovery_intervals = adjusted_recovery_intervals[
            adjusted_recovery_intervals['start'].isin(remove_1m_intervals_expansion['end'])]
        adjusted_growth_intervals1 = apply_priority_to_phases_intervals(remove_1m_intervals_expansion,
                                                                        remove_1m_intervals_growth)
        adjusted_growth_intervals2 = apply_priority_to_phases_intervals(follow_recovery_intervals,
                                                                        adjusted_growth_intervals1)
        # 筛选 growth_intervals：growth 的 end 必须是 expansion 的 start
        precede_growth_intervals = adjusted_growth_intervals2[
            adjusted_growth_intervals2['end'].isin(remove_1m_intervals_expansion['start'])]
        return remove_1m_intervals_expansion, follow_recovery_intervals, precede_growth_intervals
