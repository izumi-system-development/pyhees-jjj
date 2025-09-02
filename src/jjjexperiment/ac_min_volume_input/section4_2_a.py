import numpy as np
# JJJ
from jjjexperiment.common import *

# ============================================================================
# A.6 送風機
# ============================================================================

@jjj_cloning
def get_E_E_fan_d_t(
        P_fan_rtd: float,
        V_hs_vent_d_t: Array8760,
        V_hs_supply_d_t: Array8760,
        V_hs_dsgn: float,
        q_hs_d_t: Array8760
        ) -> Array8760:
    """(37)改 暖冷房送風機消費電力

    Args:
        P_fan_rtd: 定格暖房能力運転時の送風機の消費電力 [W]
        V_hs_vent: 日付dの時刻tにおける熱源機の風量のうちの全般換気分 [m3/h]
        V_hs_supply: 日付dの時刻tにおける熱源機の風量 [m3/h]
        V_hs_dsgn: 設計風量 [m3/h]

    Returns:
        日付dの時刻tにおける1時間当たりの 送風機の消費電力量のうちの暖冷房設備への付加分（kWh/h）

    """
    E_E_fan_1_d_t = P_fan_rtd * (V_hs_supply_d_t / V_hs_dsgn) * 10 ** (-3)
    E_E_fan_2_d_t = P_fan_rtd * (V_hs_vent_d_t / V_hs_dsgn) * 10 ** (-3)

    assert E_E_fan_1_d_t.shape == (8760,), "想定外の行列数"
    assert E_E_fan_2_d_t.shape == (8760,), "想定外の行列数"

    E_E_fan_H_d_t = np.zeros(24 * 365)
    E_E_fan_H_d_t[q_hs_d_t > 0]  \
        = np.maximum(E_E_fan_1_d_t, E_E_fan_2_d_t)[q_hs_d_t > 0]

    assert E_E_fan_H_d_t.shape == (8760,), "想定外の行列数"
    return E_E_fan_H_d_t
