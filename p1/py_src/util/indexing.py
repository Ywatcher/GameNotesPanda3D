# -*- coding: utf-8-*-

import numpy as np
import torch


def loop_bound_idx(tot:int, idx:int) -> int:
    return idx % tot


def tup2cnt(shape, row:int, col:int) -> int:  # FIXME
    tot_row, tot_col = shape[0], shape[1]
    row_ = loop_bound_idx(tot_row, row)
    col_ = loop_bound_idx(tot_col, col)

    cnt = row_*tot_col + col_
    return cnt
