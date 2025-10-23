from pyhees.section4_2_a import get_f_SFP
# JJJ
from jjjexperiment.common import *
import jjjexperiment.constants as jjj_consts

def _calc_polynomial_4th(x, coeffs):
    """4次多項式の計算"""
    a4, a3, a2, a1, a0 = coeffs
    return a4 * x**4 + a3 * x**3 + a2 * x**2 + a1 * x + a0

def _calc_E_E_fan_d_t(q_hs_d_t, V_hs_vent_d_t, f_SFP, coeffs):
    """共通のファン電力計算ロジック"""
    x = q_hs_d_t / 1000  # WARNING: 例外的に四次式では kW 単位で計算しています
    P_fan_d_t = _calc_polynomial_4th(x, coeffs)
    fx = (P_fan_d_t - f_SFP * V_hs_vent_d_t) * 10**(-3)

    E_E_fan_d_t = np.zeros(24 * 365)
    E_E_fan_d_t[q_hs_d_t > 0] = np.clip(fx[q_hs_d_t > 0], 0, None)
    return E_E_fan_d_t

@jjj_cloning
def get_E_E_fan_H_d_t(V_hs_vent_d_t, q_hs_H_d_t, f_SFP):
    """(37)改 潜熱評価モデル版

    Args:
      V_hs_vent_d_t: 日付dの時刻tにおける熱源機の風量のうちの全般換気分 [m3/h]
      q_hs_H_d_t: 日付dの時刻tにおける1時間当たりの熱源機の平均暖房能力 [W]
      f_SFP: ファンの比消費電力 [W/(m3・h)]

    Returns:
      日付dの時刻tにおける1時間当たり 送風機の消費電力量のうちの暖房設備への付加分 [kWh/h]
    """
    f_SFP = get_f_SFP(f_SFP)
    coeffs = (
        jjj_consts.P_fan_H_d_t_a4,
        jjj_consts.P_fan_H_d_t_a3,
        jjj_consts.P_fan_H_d_t_a2,
        jjj_consts.P_fan_H_d_t_a1,
        jjj_consts.P_fan_H_d_t_a0
    )
    return _calc_E_E_fan_d_t(q_hs_H_d_t, V_hs_vent_d_t, f_SFP, coeffs)

@jjj_cloning
def get_E_E_fan_C_d_t(V_hs_vent_d_t, q_hs_C_d_t, f_SFP):
    """(38)改 潜熱評価モデル版

    Args:
      V_hs_vent_d_t: 日付dの時刻tにおける熱源機の風量のうちの全般換気分 [m3/h]
      q_hs_C_d_t: 日付dの時刻tにおける1時間当たりの熱源機の平均冷房能力 [W]
      f_SFP: ファンの比消費電力 [W/(m3・h)]

    Returns:
      日付dの時刻tにおける1時間当たり 送風機の消費電力量のうちの冷房設備への付加分 [kWh/h]
    """
    f_SFP = get_f_SFP(f_SFP)
    coeffs = (
        jjj_consts.P_fan_C_d_t_a4,
        jjj_consts.P_fan_C_d_t_a3,
        jjj_consts.P_fan_C_d_t_a2,
        jjj_consts.P_fan_C_d_t_a1,
        jjj_consts.P_fan_C_d_t_a0
    )
    return _calc_E_E_fan_d_t(q_hs_C_d_t, V_hs_vent_d_t, f_SFP, coeffs)
