import numpy as np
from jjjexperiment.common import *

# ============================================================================
# A.6 送風機
# ============================================================================

def get_E_E_fan_d_t(
        P_fan_rtd: float,
        V_hs_vent_d_t: Array8760,
        V_hs_supply_d_t: Array8760,
        V_hs_dsgn: float
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

    assert E_E_fan_1_d_t.shape == (8760,), "Invalid Shape: E_E_fan_H1_d_t"
    assert E_E_fan_2_d_t.shape == (8760,), "Invalid Shape: E_E_fan_H2_d_t"

    E_E_fan_H_d_t = np.maximum(E_E_fan_1_d_t, E_E_fan_2_d_t)
    return E_E_fan_H_d_t
