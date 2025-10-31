# JJJ
from jjjexperiment.common import *
from jjjexperiment.inputs.options import *

# ============================================================================
# A.6 送風機
# ============================================================================

@jjj_cloning
def get_E_E_fan_d_t(
        E_E_fan_logic: ファン消費電力算定方法,
        P_fan_rtd: float,
        V_hs_vent_d_t: Array8760,  # NOTE: V_hs_vent として V_hs_min が入る
        V_hs_supply_d_t: Array8760,
        V_hs_dsgn: float,
        q_hs_d_t: Array8760,
        E_E_fan_min: float
        ) -> float:
    """(37)改 日付dの時刻tにおける1時間当たり 送風機の消費電力量のうちの暖房設備への付加分 [kWh/h]

    Args:
        E_E_fan_logic: ファン消費電力算定方法
        P_fan_rtd: 定格暖房能力運転時の送風機の消費電力 [W]
        V_hs_vent_d_t: 日付dの時刻tにおける熱源機の風量のうちの全般換気分 [m3/h]
        V_hs_supply_d_t: 日付dの時刻tにおける熱源機の風量 [m3/h]
        V_hs_dsgn: 設計風量 [m3/h]
        q_hs_d_t: 単時点 熱源機の平均能力 [W]
        E_E_fan_min: 最低電力直接入力値 [W]

    Returns:
        単時点 送風機の消費電力量のうちの暖冷房設備への付加分 [kWh/h]
    """
    # NOTE: 本式の利用は 最低風量・最低電力 ともに直接入力ありに限られる

    # サーモOFFの時 V_hs_vent_d_t (V_hs_min) に置き換え
    V_hs_supply_d_t = np.where(q_hs_d_t <= 0,
                        V_hs_vent_d_t,
                        np.maximum(V_hs_supply_d_t, V_hs_vent_d_t))

    # 最低
    x1_d_t = V_hs_vent_d_t
    y1 = E_E_fan_min
    # 定格
    x2 = V_hs_dsgn
    y2 = P_fan_rtd

    match E_E_fan_logic:
        case ファン消費電力算定方法.直線近似法:
            a, b = _solve_linear_system(x1_d_t, x2, y1, y2)
            E_E_fan = a * V_hs_supply_d_t + b
            return np.maximum(E_E_fan * 1e-3, 0.0)  # [kW]

        case ファン消費電力算定方法.風量三乗近似法:
            a, b = _solve_cubic_system(x1_d_t, x2, y1, y2)
            E_E_fan = a * V_hs_supply_d_t**3 + b
            return np.maximum(E_E_fan * 1e-3, 0.0)  # [kW]

        case _:
            raise ValueError("Invalid E_E_fan_logic")

def _solve_linear_system(x1, x2, y1, y2):
    """連立方程式 y = a*x + b を解く"""
    a = (y2 - y1) / (x2 -x1)
    b = y1 - a * x1
    return a, b

def _solve_cubic_system(x1, x2, y1, y2):
    """連立方程式 y = a*x^3 + b を解く"""
    a = (y2 - y1) / (x2**3 - x1**3)
    b = y1 - a * (x1**3)
    return a, b
