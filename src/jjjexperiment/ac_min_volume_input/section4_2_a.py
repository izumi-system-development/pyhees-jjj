import sympy as sp
# JJJ
from jjjexperiment.common import *
from jjjexperiment.options import *

# ============================================================================
# A.6 送風機
# ============================================================================

@jjj_cloning
def get_E_E_fan(
        E_E_fan_logic: ファン消費電力算定方法,
        P_fan_rtd: float,
        V_hs_vent: float,  # NOTE: V_hs_vent として V_hs_min が入る
        V_hs_supply: float,
        V_hs_dsgn: float,
        q_hs: float,
        E_E_fan_min: float
        ) -> float:
    """(37)改 暖冷房送風機消費電力 単時点版

    Args:
        E_E_fan_logic: ファン消費電力算定方法
        P_fan_rtd: 定格暖房能力運転時の送風機の消費電力 [W]
        V_hs_vent: 日付dの時刻tにおける熱源機の風量のうちの全般換気分 [m3/h]
        V_hs_supply: 日付dの時刻tにおける熱源機の風量 [m3/h]
        V_hs_dsgn: 設計風量 [m3/h]
        q_hs: 単時点 熱源機の平均能力 [W]
        E_E_fan_min: 最低電力直接入力値 [W]

    Returns:
        単時点 送風機の消費電力量のうちの暖冷房設備への付加分 [kWh/h]
    """
    # サーモOFFの時 V_hs_vent_d_t (V_hs_min) に置き換え
    V_hs_supply = V_hs_vent if q_hs <= 0 else max(V_hs_supply, V_hs_vent)

    x1, y1 = V_hs_vent, E_E_fan_min  # 最低
    x2, y2 = V_hs_dsgn, P_fan_rtd  # 定格

    match E_E_fan_logic:
        case ファン消費電力算定方法.直線近似法:
            a, b = _solve_linear_system(x1, x2, y1, y2)
            E_E_fan = a * V_hs_supply + b
            return max(float(E_E_fan) * 10**(-3), 0.0)  # [kW]

        case ファン消費電力算定方法.風量三乗近似法:
            a, b = _solve_cubic_system(x1, x2, y1, y2)
            E_E_fan = a * V_hs_supply**3 + b
            return max(float(E_E_fan) * 10**(-3), 0.0)  # [kW]

        case _:
            ValueError

def _solve_linear_system(x1, x2, y1, y2):
    """連立方程式 y = a*x + b を解く"""
    a, b = sp.symbols('a b')

    # 連立方程式を設定
    eq1 = sp.Eq(a * x1 + b, y1)  # y1 = a*x1 + b
    eq2 = sp.Eq(a * x2 + b, y2)  # y2 = a*x2 + b

    # 解を求める
    solution = sp.solve([eq1, eq2], [a, b])
    return solution[a], solution[b]

def _solve_cubic_system(x1, x2, y1, y2):
    """将来用: y = a*x^3 + b を解く"""
    a, b = sp.symbols('a b')

    eq1 = sp.Eq(a * x1**3 + b, y1)
    eq2 = sp.Eq(a * x2**3 + b, y2)

    solution = sp.solve([eq1, eq2], [a, b])
    return solution[a], solution[b]
