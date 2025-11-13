import numpy as np

import pyhees.section3_1 as ld
# JJJ
from jjjexperiment.common import *
import jjjexperiment.constants as jjj_consts

def get_C_BR_i(A_HCZ_i: Array5x1) -> Array5x1:
    """標準住戸との床面積比率で熱容量を求める

    Args:
        A_HCZ_i: 暖冷房区画i毎の居室の床面積 [m2]

    Returns:
        暖冷房区画i毎の 居室の熱容量 [J/K]
    """
    # 事前条件: 次数チェック
    assert A_HCZ_i.shape == (5, 1), "A_HCZ_i の行列数が想定外"

    # 標準住戸における居室の床面積 [m2]
    A_HCZ_R_i = np.array([ld.get_A_HCZ_R_i(i) for i in range(1, 6)]).reshape(5, 1)
    assert A_HCZ_R_i.shape == (5, 1), "A_HCZ_R_i の行列数が想定外"

    # 標準住戸における居室の熱容量 [J/K]
    C_BR_R_i = np.array(jjj_consts.C1_BR_R_i).reshape(5, 1)
    assert C_BR_R_i.shape == (5, 1), "C_BR_R_i の行列数が想定外"

    # CHECK: 床面積比で計算しており、天井高は共通という前提となっています
    cbri = (A_HCZ_i / A_HCZ_R_i) * C_BR_R_i
    # ([m2] / [m2]) * [J/K] = [J/K]

    # 事後条件: 次数チェック
    assert cbri.shape == (5, 1), "cbriの行列数が想定外"
    return cbri


def get_C_NR(A_NR: float) -> float:
    """標準住戸との比較で熱容量を求める

    Args:
        A_NR: 非居室の床面積 [m2]

    Returns:
        非居室の熱容量 [J/K]
    """
    # 標準住戸における非居室の熱容量 [J/K]
    C_NR_R = jjj_consts.C1_NR_R

    # CHECK: 床面積比で計算しており、天井高は共通という前提となっています
    return (A_NR / jjj_consts.A_NR_R) * C_NR_R
    # ([m2] / [m2]) * [J/K] = [J/K]
