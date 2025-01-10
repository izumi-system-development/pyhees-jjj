import numpy as np
from nptyping import NDArray, Float64, Shape

from pyhees.section4_2 import *
# JJJ
import jjjexperiment.carryover_heat as jjj_carryover_heat


# tを除外して単一時点での計算とする
# calc_carryover_H, calc_carryover_C に分割して定義する
def calc_carryover(
        region,
        A_HCZ_i: NDArray[Shape["5"], Float64],
        Theta_star_HBR_d_t: NDArray[Shape["8760"], Float64],
        Theta_HBR_d_t_i: NDArray[Shape["5, 8760"], Float64],
        t: int) -> NDArray[Shape["5, 1"], Float64]:
    """過剰熱量 [MJ]

    Args:
        region: 地域区分
        A_HCZ_i: 暖冷房区画iの床面積 [m2]
        Theta_star_HBR_d_t: 日付dの時刻tにおける 負荷バランス時の居室の室温 [℃]
        Theta_HBR_d_t_i: 日付dの時刻tにおける 暖冷房区画iの室温 [℃]
        t: 時刻
    """
    # 実行条件: 先頭時刻の熱繰越は考えない
    if t <= 0: return np.zeros((5, 1))

    A_HCZ_i = A_HCZ_i.reshape(-1,1)  # (5,) -> (5, 1)
    cbri = jjj_carryover_heat.get_C_BR_i(A_HCZ_i)
    assert cbri.shape == (5, 1), "cbriの行列数が想定外"

    # NOTE: region の代わりに temperature_diff の正負で暖冷を判断することも可能
    # なお、デフォルト条件では結果に変化なし

    H, C, M = get_season_array_d_t(region)
    temperature_diff = Theta_HBR_d_t_i[:, t-1:t] - Theta_star_HBR_d_t[t-1]

    if H[t] and C[t]:
        raise ValueError("想定外の季節")
    # 暖房期
    elif H[t] and Theta_HBR_d_t_i[:, t-1:t] > Theta_star_HBR_d_t[t-1]:
        temperature_diff = Theta_HBR_d_t_i[:, t-1:t] - Theta_star_HBR_d_t[t]
    # 冷房期
    elif C[t] and Theta_HBR_d_t_i[:, t-1:t] < Theta_star_HBR_d_t[t-1]:
        temperature_diff = Theta_star_HBR_d_t[t-1] - Theta_HBR_d_t_i[:, t:t+1]
    else:
        return np.zeros((5, 1))

    # 事後条件:
    assert np.all(0 <= cbri), "居室の熱容量は負にならない"
    assert np.all(0 <= temperature_diff), "ここで温度差は正になるよう算出"

    return cbri * temperature_diff / 1_000_000  # J/h -> MJ/h

# NOTE:
# MATRIX[:, t] -> Shape(5, )
# MATRIX[:, t:t+1] -> Shape(5, 1)

@log_res(['L_star_CS_i'])
def get_L_star_CS_i_2023(
        L_CS_d_t_i, Q_star_trs_prt_d_t_i, region,
        carryover: NDArray[Shape["5, 1"], Float64],
        t: int
    )-> NDArray[Shape["5, 1"], Float64]:
    """t時点計算版 (9-1)(9-2)(9-3) get_L_star_CS_d_t_i

    Args:
        L_CS_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの 冷房顕熱負荷 [MJ/h]
        Q_star_trs_prt_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの 熱損失を含む負荷バランス時の非居室への熱移動 [MJ/h]
        region: 地域区分
        carryover: 過剰熱量 [MJ]
        t: 日付時刻インデックス

    Returns:
        暖冷房区画iの一時点の 熱損失を含む負荷バランス時の冷房顕熱負荷 [MJ]
    """
    # 実行条件: 指定時刻tが冷房期である
    H, C, M = get_season_array_d_t(region)
    if not C[t]: return np.zeros((5, 1))

    L_CS_i = L_CS_d_t_i[:5, t:t+1]
    assert L_CS_i.shape == (5, 1), "L_CS_iの行列数が想定外"
    Cf = 0 < L_CS_i

    # マスクが二次元のときは L_star_CS_i[Cf] ではなく np.where を使用した方が簡潔なコードになる

    # 負荷から過剰熱量分を差し引く
    L_star_CS_i = L_CS_i + Q_star_trs_prt_d_t_i[:5, t:t+1] - carryover
    L_star_CS_i = np.clip(L_star_CS_i, 0, None)
    L_star_CS_i = np.where(Cf, L_star_CS_i, np.zeros((5, 1)))
    return L_star_CS_i


@log_res(['L_star_H_i'])
def get_L_star_H_i_2023(
        L_H_d_t_i, Q_star_trs_prt_d_t_i, region,
        carryover: NDArray[Shape["5, 1"], Float64],
        t: int
    )-> NDArray[Shape["5, 1"], Float64]:
    """t時点計算版 (8-1)(8-2)(8-3) get_L_star_H_d_t_i

    Args:
        L_H_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの 暖房負荷 [MJ/h]
        Q_star_trs_prt_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの 熱損失を含む負荷バランス時の非居室への熱移動 [MJ/h]
        region: 地域区分
        carryover: 過剰熱量 [MJ]
        t: 日付時刻インデックス

    Returns:
        暖冷房区画iの一時点の 熱損失を含む負荷バランス時の暖房負荷 [MJ]
    """
    # 実行条件: 指定時刻tが暖房期である
    H, C, M = get_season_array_d_t(region)
    if not H[t]: return np.zeros((5, 1))

    L_H_i = L_H_d_t_i[:5, t:t+1]
    assert L_H_i.shape == (5, 1), "L_H_iの行列数が想定外"
    Hf = 0 < L_H_i

    # マスクが二次元のときは L_star_H_i[Hf] ではなく np.where を使用した方が簡潔なコードになる

    # 負荷から過剰熱量分を差し引く
    L_star_H_i = L_H_i + Q_star_trs_prt_d_t_i[:5, t:t+1] - carryover
    L_star_H_i = np.clip(L_star_H_i, 0, None)
    L_star_H_i = np.where(Hf, L_star_H_i, np.zeros((5, 1)))
    return L_star_H_i
