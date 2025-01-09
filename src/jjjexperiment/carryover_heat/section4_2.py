import numpy as np
from typing import Tuple
from nptyping import NDArray, Float64, Shape

from pyhees.section4_2 import *


@log_res(['L_star_CS_i'])
def get_L_star_CS_i_2023(
        L_CS_d_t_i, Q_star_trs_prt_d_t_i, region,
        A_HCZ_i, A_HCZ_R_i, Theta_star_HBR_d_t, Theta_HBR_d_t_i, t: int
    )-> NDArray[Shape["5, 1"], Float64]:
    """t時点計算版 get_L_star_CS_d_t_i

    Args:
        L_CS_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの 冷房顕熱負荷 [MJ/h]
        Q_star_trs_prt_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの 熱損失を含む負荷バランス時の非居室への熱移動 [MJ/h]
        region: 地域区分

        A_HCZ_i: 暖冷房区画iの床面積 [m2]
        A_HCZ_R_i: 標準住戸における暖冷房区画の床面積 [m2]
        Theta_star_HBR_d_t: 暖冷房区画iの熱損失係数 [W/m2K]
        Theta_HBR_d_t_i: 暖冷房区画iの室温 [℃]
        t: 時刻

    Returns:
        一時点の 日付dの時刻tにおける暖冷房区画iの1時間当たりの 熱損失を含む負荷バランス時の冷房顕熱負荷
    """
    H, C, M = get_season_array_d_t(region)
    L_CS_d_t_i = L_CS_d_t_i[:5]
    f = L_CS_d_t_i > 0
    Cf = np.logical_and(C, f)[:, t]  # 5x1

    A_HCZ_i = A_HCZ_i.reshape(-1,1)
    A_HCZ_R_i = A_HCZ_R_i.reshape(-1,1)

    if 0 < t:
        cbri = get_C_BR_i(A_HCZ_i, A_HCZ_R_i)
        arr_theta = np.clip(Theta_star_HBR_d_t[t-1] - Theta_HBR_d_t_i[:, t-1:t], 0, None)  # 5x1
        carry_over = cbri * arr_theta / 1_000_000  # 過剰熱量: J/h -> MJ/h
    else:
        carry_over = np.zeros((5, 1))

    if np.any(carry_over < 0):
        pass
    assert np.all(np.greater_equal(carry_over, 0)), "想定外の計算結果(過剰熱量がマイナス)"

    # <負荷バランス時の暖房負荷> - <過剰熱量>
    # NOTE: MATRIX[:, 0] だと shape(5, ) となりダメ MATRIX[:, 0:1] と書くと shape(5,1)
    arr = L_CS_d_t_i[:, t:t+1] + Q_star_trs_prt_d_t_i[:, t:t+1] - carry_over

    L_star_CS_i = np.zeros((5, 1))
    L_star_CS_i[Cf] = np.clip(arr, 0, None)[Cf]
    return L_star_CS_i


@log_res(['L_star_H_i'])
def get_L_star_H_i_2023(
        L_H_d_t_i,
        Q_star_trs_prt_d_t_i,
        region,
        A_HCZ_i,
        A_HCZ_R_i,
        Theta_star_HBR_d_t,
        Theta_HBR_d_t_i,
        t: int
    )-> NDArray[Shape["5, 1"], Float64]:
    """t時点計算版 get_L_star_H_d_t_i

    Args:
        L_H_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの 暖房負荷 [MJ/h]
        Q_star_trs_prt_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの 熱損失を含む負荷バランス時の非居室への熱移動 [MJ/h]
        region: 地域区分

        A_HCZ_i: 暖冷房区画iの床面積 [m2]
        A_HCZ_R_i: 標準住戸における暖冷房区画の床面積 [m2]
        Theta_star_HBR_d_t: 暖冷房区画iの熱損失係数 [W/m2K]
        Theta_HBR_d_t_i: 暖冷房区画iの室温 [℃]
        t: 時刻

    Returns:
        日付dの時刻tにおける暖冷房区画iの1時間当たりの 熱損失を含む負荷バランス時の暖房負荷
    """
    H, C, M = get_season_array_d_t(region)
    L_H_d_t_i = L_H_d_t_i[:5]
    f = L_H_d_t_i > 0
    Hf = np.logical_and(H, f)[:, t:t+1]  # 5x1

    A_HCZ_i = A_HCZ_i.reshape(-1,1)
    A_HCZ_R_i = A_HCZ_R_i.reshape(-1,1)

    if 0 < t:
        cbri = get_C_BR_i(A_HCZ_i, A_HCZ_R_i)
        arr_theta = np.clip(Theta_HBR_d_t_i[:, t-1:t] - Theta_star_HBR_d_t[t-1], 0, None)  # 5x1
        carry_over = cbri * arr_theta / 1_000_000  # 過剰熱量: J/h -> MJ/h
    else:
        carry_over = np.zeros((5, 1))
    assert np.all(np.greater_equal(carry_over, 0)), "想定外の計算結果(過剰熱量がマイナス)"

    # <負荷バランス時の暖房負荷> - <過剰熱量>
    arr = L_H_d_t_i[:, t:t+1] + Q_star_trs_prt_d_t_i[:, t:t+1] - carry_over

    L_star_H_i = np.zeros((5, 1))
    L_star_H_i[Hf] = arr[Hf]
    return L_star_H_i
