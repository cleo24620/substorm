# encoding = UTF-8
"""
@USER: cleo
@DATE: 2024/10/15
@DESCRIPTION: short funcs
"""
import re


def get_fn_time(fn: str) -> str:
    """
    get time from filename
    @param fn: the filename
    @return:
    """
    match = re.search(r"\d{6}", fn)
    return match.group(0)
