from nptyping import Float64, NDArray, Shape
import numpy as np

import pyhees.section3_1 as ld
import pyhees.section3_1_e as algo
import pyhees.section3_2 as gihi
import pyhees.section4_2 as dc
import pyhees.section11_1 as rgn
import pyhees.section11_2 as slr
# JJJ
from jjjexperiment.common import *

def calc_Theta_uf(
        L_H_flr1st: float,
        A_s_ufvnt: float,
        Theta_in: float,
        Theta_ex: float,
        V_flr1st: float,
        ) -> float:
    """床下空間の温度 (40-4) 単時点

    Args:
        L_H_flr1st: 一階部分の1時間当たりの暖房負荷 [MJ/h]
        A_s_ufvnt: 空気を供給する床下空間に接する床の面積 [m2]
        Theta_in: 室温 [℃]
        Theta_ex: 外気温度 [℃]
        V_flr1st: 第1床面積 [m2]
    Returns:
        床下空間の温度 [℃]
    """
    ro_air = dc.get_ro_air()    # 空気密度 [kg/m3]
    c_p_air = algo.get_c_p_air()  # 空気の比熱 [kJ/kgK]
    U_s = dc.get_U_s()          # 床の熱貫流率 [W/m2K]

    H_floor = 0.7  # 床の温度差係数(-) 損失として

    a1 = L_H_flr1st * 1e+3
    a2 = U_s * A_s_ufvnt * (Theta_in - Theta_ex) * H_floor * 3.6
    a3 = Theta_in * (ro_air * c_p_air * V_flr1st + U_s * A_s_ufvnt * 3.6)
    b1 = ro_air * c_p_air * V_flr1st + U_s * A_s_ufvnt * 3.6

    Theta_uf = (a1 - a2 + a3) / b1
    return Theta_uf


@jjj_clone
def calc_Q_hat_hs(
        Q: float,
        A_A: float,
        V_vent_l: float,
        V_vent_g_i: NDArray[Shape["5, 1"], Float64],
        mu_H: float,
        mu_C: float,
        J: float,
        q_gen: float,
        n_p: float,
        q_p_H: float,
        q_p_CS: float,
        q_p_CL: float,
        X_ex: float,
        w_gen: float,
        Theta_ex: float,
        L_wtr: float,
        HCM: JJJ_HCM  # regionの代替
        ) -> float:
    """単時点版 (40-1a)(40-1b)(40-2a)(40-2b)(40-2c)(40-3)

    Args:
        Q: 当該住戸の熱損失係数 [W/(m2・K)]
        A_A: 床面積の合計 [m2]
        V_vent_l: 局所換気量 [m3/h]
        V_vent_g_i: 暖冷房区画iの全般換気量 [m3/h]
        mu_H: 当該住戸の暖房期の日射取得係数 [(W/m2)/(W/m2)]
        mu_C: 当該住戸の冷房期の日射取得係数 [(W/m2)/(W/m2)]
        J: 水平面全天日射量 [W/m2]
        q_gen: 内部発熱 [W]
        n_p: 在室人数 [人]
        q_p_H: 暖房期における人体からの1人当たりの顕熱発熱量 [W/人]
        q_p_CS: 冷房期における人体からの1人当たりの顕熱発熱量 [W/人]
        q_p_CL: 冷房期における人体からの1人当たりの潜熱発熱量 [W/人]
        X_ex: 外気の絶対湿度 [kg/kg(DA)]
        w_gen: 内部発湿量 [kg/h]
        Theta_ex: 外気温度（℃）
        L_wtr: 水の蒸発潜熱 [kJ/kg]
        HCM: 季節区分

    Returns:
        (時点)１時間当たりの熱源機の風量を計算するための熱源機の暖房出力 [MJ/h]
    """
    c_p_air = dc.get_c_p_air()
    rho_air = dc.get_rho_air()
    Theta_set_H = dc.get_Theta_set_H()
    Theta_set_C = dc.get_Theta_set_C()
    X_set_C = dc.get_X_set_C()

    match HCM:
        case JJJ_HCM.H:
            # (40-1b)
            Q_hat_hs_H = (
                (Q - 0.35 * 0.5 * 2.4) * A_A  # 外皮
                + (c_p_air * rho_air * (V_vent_l + np.sum(V_vent_g_i))) / 3600  # 換気
                ) * (Theta_set_H - Theta_ex)
            Q_hat_hs_H -= mu_H * A_A * J  # 日射
            Q_hat_hs_H -= q_gen  # 内部発熱
            Q_hat_hs_H -= n_p * q_p_H  # 人体発熱
            # (40-1a)
            return max(Q_hat_hs_H * 3600 * 1e-6, 0)

        case JJJ_HCM.C:
            # (40-2b)
            Q_hat_hs_CS = (
                ((Q - 0.35 * 0.5 * 2.4) * A_A
                + (c_p_air * rho_air * (V_vent_l + np.sum(V_vent_g_i))) / 3600
                ) * (Theta_ex - Theta_set_C) \
                + mu_C * A_A * J \
                + q_gen \
                + n_p * q_p_CS) * 3600 * 1e-6
            # (40-2c)
            Q_hat_hs_CL = (
                (rho_air * (V_vent_l + np.sum(V_vent_g_i)) * (X_ex - X_set_C) * 10^3 + w_gen) * L_wtr \
                + n_p * q_p_CL * 3600) * 1e-6
            # (40-2a)
            return (max(Q_hat_hs_CS, 0) + max(Q_hat_hs_CL, 0))

        case JJJ_HCM.M:
            # (40-3)
            return 0

        case _:
            raise ValueError("Invalid season flag")
