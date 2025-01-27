import numpy as np
from nptyping import NDArray, Shape, Float64
# JJJ
import jjjexperiment.constants as jjj_consts

def get_C_BR_i(
        A_HCZ_i: NDArray[Shape["5, 1"], Float64],
        calc_mode: int = 1
    )-> NDArray[Shape["5, 1"], Float64]:
    """標準住戸との比較で熱容量を求める

    Args:
        A_HCZ_i: 暖冷房区画i毎の居室の床面積 [m2]
        calc_mode: 熱容量計算式の切替(1:空間・什器のみ, 2:壁・床・天井を含む)

    Returns:
        暖冷房区画i毎の 居室の熱容量 [J/K]
    """
    is_default = calc_mode == 1

    # 標準住戸における居室の床面積 [m2]
    A_HCZ_R_i = np.array([
        [jjj_consts.A_HCZ_R_i[0]],
        [jjj_consts.A_HCZ_R_i[1]],
        [jjj_consts.A_HCZ_R_i[2]],
        [jjj_consts.A_HCZ_R_i[3]],
        [jjj_consts.A_HCZ_R_i[4]],
    ])
    # 標準住戸における居室の熱容量 [J/K]
    C_BR_R_i = np.array([
        [jjj_consts.C1_BR_R_i[0]],
        [jjj_consts.C1_BR_R_i[1]],
        [jjj_consts.C1_BR_R_i[2]],
        [jjj_consts.C1_BR_R_i[3]],
        [jjj_consts.C1_BR_R_i[4]],
    ] if is_default else [
        [jjj_consts.C2_BR_R_i[0]],
        [jjj_consts.C2_BR_R_i[1]],
        [jjj_consts.C2_BR_R_i[2]],
        [jjj_consts.C2_BR_R_i[3]],
        [jjj_consts.C2_BR_R_i[4]],
    ])

    # 事前条件: 次数チェック
    assert A_HCZ_i.shape == (5, 1), "A_HCZ_iの行列数が想定外"

    # CHECK: 床面積比で計算しており、天井高は共通という前提となっています
    cbri = (A_HCZ_i / A_HCZ_R_i) * C_BR_R_i
    # ([m2] / [m2]) * [J/K] = [J/K]

    # 事後条件: 次数チェック
    assert cbri.shape == (5, 1), "cbriの行列数が想定外"
    return cbri


def get_C_NR(
        A_NR: float,
        calc_mode: int = 1
    ) -> float:
    """標準住戸との比較で熱容量を求める

    Args:
        A_NR: 非居室の床面積 [m2]
        calc_mode: 熱容量計算式の切替(1:空間・什器のみ, 2:壁・床・天井を含む)

    Returns:
        非居室の熱容量 [J/K]
    """
    is_default = calc_mode == 1

    # 標準住戸における非居室の熱容量 [J/K]
    C_NR_R = jjj_consts.C1_NR_R if is_default else jjj_consts.C2_NR_R

    # CHECK: 床面積比で計算しており、天井高は共通という前提となっています
    return (A_NR / jjj_consts.A_NR_R) * C_NR_R
    # ([m2] / [m2]) * [J/K] = [J/K]
