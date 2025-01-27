import numpy as np
from nptyping import NDArray, Float64, Shape

import pyhees.section4_2 as dc
# JJJ
import jjjexperiment.carryover_heat as jjj_carryover_heat
from jjjexperiment.logger import log_res

def calc_carryover(
        H: bool,
        C: bool,
        A_HCZ_i: NDArray[Shape["5"], Float64],
        Theta_HBR_i: NDArray[Shape["5, 1"], Float64],
        Theta_star_HBR: float,
    ) -> NDArray[Shape["5, 1"], Float64]:
    """過剰熱量 [MJ] (一時点)

    Args:
        H: 暖房期
        C: 冷房期
        A_HCZ_i: 暖冷房区画iの床面積 [m2]
        Theta_star_HBR: 負荷バランス時の居室の室温 [℃]
        Theta_HBR_d_t_i: 暖冷房区画iの室温 [℃]
    """
    # 事前条件: 次数チェック
    assert A_HCZ_i.shape == (5,), "A_HCZ_iの次数が想定外"
    assert Theta_HBR_i.shape == (5, 1), "Theta_HBR_iの次数が想定外"

    # 熱容量の取得
    A_HCZ_i = A_HCZ_i.reshape(-1,1)  # (5,) -> (5, 1)
    cbri = jjj_carryover_heat.get_C_BR_i(A_HCZ_i)

    # 季節の判断
    if H and C:
        raise ValueError("想定外の季節")
    elif H:
        temperature_diff = Theta_HBR_i - Theta_star_HBR
    elif C:
        temperature_diff = Theta_star_HBR - Theta_HBR_i
    else:
        # 空調なし -> 過剰熱量なし
        return np.zeros((5, 1))

    # 事後条件:
    assert np.all(0 <= cbri), "居室の熱容量は負にならない"
    assert np.all(0 <= temperature_diff), "ここで温度差は正になるよう算出"

    return cbri * temperature_diff / 1_000_000  # J/h -> MJ/h

# NOTE:
# MATRIX[:, t] -> Shape(5, )
# MATRIX[:, t:t+1] -> Shape(5, 1)

@log_res(['L_star_H_i'])
def get_L_star_H_i_2024(
        H: bool,
        L_H_i: NDArray[Shape["5, 1"], Float64],
        Q_star_trs_prt_i: NDArray[Shape["5, 1"], Float64],
        carryover: NDArray[Shape["5, 1"], Float64],
    )-> NDArray[Shape["5, 1"], Float64]:
    """(8-1)(8-2)(8-3) -> 時点版, 過剰熱量を考慮

    Args:
        H: 暖房期
        L_H_i: (時点)暖冷房区画iの1時間当たりの 暖房負荷 [MJ/h]
        Q_star_trs_prt_i: (時点)暖冷房区画iの1時間当たりの 熱損失を含む負荷バランス時の非居室への熱移動 [MJ/h]
        carryover: 過剰熱量 [MJ]

    Returns:
        暖冷房区画iの一時点の 熱損失を含む負荷バランス時の暖房負荷 [MJ]
    """
    # 実行条件: 指定時刻tが暖房期である
    assert L_H_i.shape == (5, 1), "L_H_iの行列数が想定外"
    if not H or np.all(L_H_i <= 0):
        return np.zeros((5, 1))

    # 繰越熱量は負荷低減に働く
    L_star_H_i = L_H_i + Q_star_trs_prt_i - carryover
    L_star_H_i = np.clip(L_star_H_i, 0, None)

    # 事後条件:
    assert np.all(0 <= L_star_H_i), "負荷バランス時の暖房負荷は負にならない"
    return L_star_H_i

@log_res(['L_star_CS_i'])
def get_L_star_CS_i_2024(
        C: bool,
        L_CS_i: NDArray[Shape["5, 1"], Float64],
        Q_star_trs_prt_i: NDArray[Shape["5, 1"], Float64],
        carryover: NDArray[Shape["5, 1"], Float64],
    )-> NDArray[Shape["5, 1"], Float64]:
    """(9-1)(9-2)(9-3) -> 時点版, 過剰熱量を考慮

    Args:
        C: 冷房期
        L_CS_i: (時点)暖冷房区画iの1時間当たりの 冷房顕熱負荷 [MJ/h]
        Q_star_trs_prt_i: (時点)暖冷房区画iの1時間当たりの 熱損失を含む負荷バランス時の非居室への熱移動 [MJ/h]
        carryover: 過剰熱量 [MJ]

    Returns:
        暖冷房区画iの一時点の 熱損失を含む負荷バランス時の冷房顕熱負荷 [MJ]
    """
    # 実行条件: 指定時刻tが暖房期である
    assert L_CS_i.shape == (5, 1), "L_CS_iの行列数が想定外"
    if not C or np.all(L_CS_i <= 0):
        return np.zeros((5, 1))

    # 繰越熱量は負荷低減に働く
    L_star_CS_i = L_CS_i + Q_star_trs_prt_i - carryover
    L_star_CS_i = np.clip(L_star_CS_i, 0, None)

    # 事後条件:
    assert np.all(0 <= L_star_CS_i), "負荷バランス時の冷房顕熱負荷は負にならない"
    return L_star_CS_i

def get_Theta_HBR_i_2023(Theta_star_HBR_d_t, V_supply_d_t_i, Theta_supply_d_t_i, U_prt, A_prt_i, Q, A_HCZ_i, L_star_H_d_t_i, L_star_CS_d_t_i, region,
                         A_HCZ_R_i, Theta_HBR_d_t_i, t: int):
    """ (46-1)(46-2)(46-3) -> 時点版, 過剰熱量を考慮

    前時刻の値を利用: \n
      Theta_star_HBR_d_t: 日付dの時刻tにおける負荷バランス時の居室の室温（℃） \n
      Theta_HBR_d_t_i: xxx \n
      V_supply_d_t_i: 日付dの時刻tにおける暖冷房区画iの吹き出し風量（m3/h） \n
      Theta_supply_d_t_i: 日付dの時刻tにおける負荷バランス時の居室の室温（℃） \n
      U_prt: 間仕切りの熱貫流率（W/(m2・K)） \n
      A_prt_i: 暖冷房区画iから見た非居室の間仕切りの面積（m2） \n
      Q: 当該住戸の熱損失係数（W/(m2・K)） \n
      A_HCZ_i: 暖冷房区画iの床面積（m2） \n
      L_star_H_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの間仕切りの熱取得を含む実際の暖房負荷（MJ/h） \n
      L_star_CS_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの間仕切りの熱取得を含む実際の冷房顕熱負荷（MJ/h） \n
      region: 地域区分 \n

    Extended Args: \n
      A_HCZ_R_i: 標準住戸における暖冷房区画の床面積[m2] \n
      idx: 時系列データにおけるインデックス \n

    Returns: \n
      (日付dの時刻tにおける)暖冷房区画iの実際の居室の室温[℃] \n

    """
    H, C, M = dc.get_season_array_d_t(region)
    c_p_air = dc.get_c_p_air()
    rho_air = dc.get_rho_air()

    # NOTE: shape(5,) -> shape(5,1)
    A_prt_i = A_prt_i.reshape(-1,1)
    A_HCZ_i = A_HCZ_i.reshape(-1,1)
    A_HCZ_R_i = A_HCZ_R_i.reshape(-1,1)

    # 暖房期 (46-1)
    if H[t]:
      # NOTE: 時系列データの最初の計算では繰り越し:なしとしています
      cbri = jjj_carryover_heat.get_C_BR_i(A_HCZ_i)
      arr_theta = (Theta_HBR_d_t_i[:, t-1:t] - Theta_star_HBR_d_t[t]) if 0 < t else 0
      capacity = cbri * arr_theta  # 熱容量[J]

      arr_above_1 = c_p_air * rho_air * V_supply_d_t_i[:, t:t+1] * (Theta_supply_d_t_i[:, t:t+1] - Theta_star_HBR_d_t[t])
      arr_above_2 = -1 * L_star_H_d_t_i[:, t:t+1] * 10 ** 6  # MJ/h -> J/h

      arr_below_1 = c_p_air * rho_air * V_supply_d_t_i[:, t:t+1]
      arr_below_2 = (U_prt * A_prt_i + Q * A_HCZ_i) * 3600

      Theta_HBR_i = Theta_star_HBR_d_t[t:t+1] \
        + (arr_above_1 + capacity + arr_above_2) / (arr_below_1 + arr_below_2 + cbri)

      # 暖冷房区画iの実際の居室の室温θ_(HBR,d,t,i)は、暖房期において負荷バランス時の居室の室温θ_(HBR,d,t)^*を下回る場合、
      # 負荷バランス時の居室の室温θ_(HBR,d,t)^*に等しい
      Theta_HBR_i = np.clip(Theta_HBR_i, Theta_star_HBR_d_t[t], None)

    # 冷房期 (46-2)
    elif C[t]:
      cbri = jjj_carryover_heat.get_C_BR_i(A_HCZ_i)
      arr_theta = (Theta_star_HBR_d_t[t] - Theta_HBR_d_t_i[:, t-1:t])
      capacity = cbri * arr_theta  # 熱容量[J]

      arr_above_1 = c_p_air * rho_air * V_supply_d_t_i[:, t:t+1] * (Theta_star_HBR_d_t[t] - Theta_supply_d_t_i[:, t:t+1])
      arr_above_2 = -1 * L_star_CS_d_t_i[:, t:t+1] * 10 ** 6

      arr_below_1 = c_p_air * rho_air * V_supply_d_t_i[:, t:t+1]
      arr_below_2 = (U_prt * A_prt_i + Q * A_HCZ_i) * 3600

      Theta_HBR_i = Theta_star_HBR_d_t[t:t+1] \
        -1 * (arr_above_1 + capacity + arr_above_2) / (arr_below_1 + arr_below_2 + cbri)

      # 冷房期において負荷バランス時の居室の室温θ_(HBR,d,t)^*を上回る場合、負荷バランス時の居室の室温θ_(HBR,d,t)^*に等しい
      Theta_HBR_i = np.clip(Theta_HBR_i, None, Theta_star_HBR_d_t[t])

    # 中間期 (46-3)
    elif M[t]:
      Theta_HBR_i = Theta_star_HBR_d_t[t:t+1]

    return Theta_HBR_i

def get_Theta_NR_2023(Theta_star_NR_d_t, Theta_star_HBR_d_t, Theta_HBR_d_t_i, A_NR, V_vent_l_NR_d_t, V_dash_supply_d_t_i, V_supply_d_t_i, U_prt, A_prt_i, Q, Theta_NR_d_t, t: int):
    """ (48a)(48b)(48c)(48d) -> 時点版, 過剰熱量を考慮

    前時刻の値を利用: \
      Theta_star_NR_d_t: 日付dの時刻tにおける実際の非居室の室温（℃） \
      Theta_NR_d_t_i: xxx \
    Extended Args:
      idx: 時系列データにおけるインデックス

    Returns:
      (日付dの時刻tにおける)実際の非居室の室温 [℃]

    """
    c_p_air = dc.get_c_p_air()
    rho_air = dc.get_rho_air()

    # NOTE: shape(5,) -> shape(5,1)
    A_prt_i = A_prt_i.reshape(-1,1)

    # (48d)
    k_dash_i = c_p_air * rho_air * (V_dash_supply_d_t_i[:, t:t+1] / 3600) + U_prt * A_prt_i  # 5x1
    # (48c)
    k_prt_i = c_p_air * rho_air * (V_supply_d_t_i[:, t:t+1] / 3600) + U_prt * A_prt_i  # 5x1
    # (48b)
    k_evp = (Q - 0.35 * 0.5 * 2.4) * A_NR + c_p_air * rho_air * (V_vent_l_NR_d_t[t] / 3600)  # 5x1

    # CHECK: 資料 Theta_NR_d_t_i -> Theta_NR_d_t が正かな?
    arr1 = -1 * np.sum(k_dash_i, axis=0) * (Theta_star_HBR_d_t[t] - Theta_star_NR_d_t[t])
    arr2 = np.sum(k_prt_i * (Theta_HBR_d_t_i[:, t:t+1] - Theta_star_NR_d_t[t]), axis=0)
    arr3 = np.sum(jjj_carryover_heat.get_C_NR(A_NR) * (Theta_NR_d_t[t-1:t] - Theta_star_NR_d_t[t]), axis=0)

    # (48a)
    arr_above = arr1 + arr2 + arr3
    arr_below = k_evp + np.sum(k_prt_i, axis=0) + np.sum(jjj_carryover_heat.get_C_NR(A_NR), axis=0)
    Theta_NR = Theta_star_NR_d_t[t] + arr_above / arr_below

    return Theta_NR