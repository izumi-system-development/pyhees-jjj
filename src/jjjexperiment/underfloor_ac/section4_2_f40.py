import pyhees.section4_2 as dc
# JJJ
from jjjexperiment.common import *

# NOTE: Q^,hs,d,t は 床下負荷増加分も見込む(2025/03)
@jjj_cloning
def calc_Q_hat_hs(
        Q: float,
        A_A: float,
        V_vent_l: float,
        sum_V_vent_g_i: float,  # vectorizeするため調整 (5,1)->(5,)
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
        sum_V_vent_g_i: 暖冷房区画iの全般換気量 [m3/h]
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
    # vectorize可能
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
                + (c_p_air * rho_air * (V_vent_l + sum_V_vent_g_i)) / 3600  # 換気
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
                + (c_p_air * rho_air * (V_vent_l + sum_V_vent_g_i)) / 3600
                ) * (Theta_ex - Theta_set_C) \
                + mu_C * A_A * J \
                + q_gen \
                + n_p * q_p_CS) * 3600 * 1e-6
            # (40-2c)
            Q_hat_hs_CL = (
                (rho_air * (V_vent_l + sum_V_vent_g_i) * (X_ex - X_set_C) * 1e+3 + w_gen) * L_wtr \
                + n_p * q_p_CL * 3600) * 1e-6
            # (40-2a)
            return (max(Q_hat_hs_CS, 0) + max(Q_hat_hs_CL, 0))

        case JJJ_HCM.M:
            # (40-3)
            return 0

        case _:
            raise ValueError("Invalid season flag")
