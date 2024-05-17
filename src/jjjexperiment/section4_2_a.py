# 改変のベースとしているモジュール
from pyhees.section4_2_a import \
    calc_e_th_mid_H, \
    calc_e_th_mid_C, \
    calc_e_th_rtd_H, \
    calc_e_th_rtd_C, \
    calc_e_th_H_d_t, \
    calc_e_th_C_d_t, \
    get_q_hs_H_d_t, \
    get_q_hs_C_d_t, \
    get_q_hs_C_d_t_2, \
    get_e_hs_H_d_t, \
    get_e_hs_C_d_t, \
    get_e_r_rtd_H, \
    get_e_r_rtd_C, \
    get_e_r_mid_H, \
    get_e_r_mid_C, \
    get_e_r_min_H, \
    get_e_r_min_C, \
    get_e_r_H_d_t, \
    get_e_r_H_d_t_2023, \
    get_e_r_C_d_t, \
    get_e_r_C_d_t_2023, \
    get_E_E_fan_H_d_t, \
    get_E_E_fan_C_d_t, \
    get_E_E_comp_H_d_t, \
    get_E_E_comp_C_d_t \

import pyhees.section4_3

import numpy as np
import pandas as pd
from datetime import datetime

from jjjexperiment.denchu_1 import Spec
from jjjexperiment.logger import LimitedLoggerAdapter as _logger  # デバッグ用ロガー
import jjjexperiment.constants as constants
from jjjexperiment.constants import PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_3, PROCESS_TYPE_4
import jjjexperiment.denchu_2 as denchu_2

@constants.jjjexperiment_clone
def calc_E_E_H_d_t(
        case_name,
        Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t,  # 空気温度
        V_hs_supply_d_t, V_hs_vent_d_t, V_hs_dsgn_H,      # 風量
        C_df_H_d_t,                                       # 暖房出力補正係数
        q_hs_min_H,                                       # 最小暖房時
        q_hs_mid_H, P_hs_mid_H, V_fan_mid_H, P_fan_mid_H,  # 中間暖房時
        q_max_C, q_max_H,                                  # 最大暖房時
        q_rtd_C, q_hs_rtd_C,                               # 定格冷房時
        q_rtd_H, e_rtd_H, P_rac_fan_rtd_H, V_fan_rtd_H, P_fan_rtd_H, q_hs_rtd_H, P_hs_rtd_H,  # 定格暖房時
        type, region, dualcompressor_H, EquipmentSpec, input_C_af_H, f_SFP_H, climateFile,  # その他
        simu_R_H=None, spec: Spec=None, Theta_real_inner=None, RH_real_inner=None):  # 電中研モデルのみ使用
    """ (1)
    Args:
        P_fan_rad_H: 定格暖房能力試験 室内側送風機の消費電力 [W]\n
        日付dの時刻tにおける\n
            V_hs_vent_d_t:   熱源機の風量のうちの全般換気分 [m3/h]\n
            V_hs_supply_d_t: 熱源機の風量 [m3/h]\n
            X_hs_in_d_t:     熱源機の入口における絶対湿度 [kg/kg(DA)]\n
    Returns:
        日付dの時刻tにおける\n
            E_E_H_d_t:     1時間当たりの暖房時の消費電力量[kWh/h]
            E_E_fan_H_d_t: 1時間当たりの暖房時消費電力量の送風機による付加分[kWh/h]
            q_hs_H_d_t:    1時間当たりの熱源機の平均暖房能力[W]
    """
    # (3) 日付dの時刻tにおける1時間当たりの熱源機の平均暖房能力(W)
    q_hs_H_d_t = get_q_hs_H_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, V_hs_supply_d_t, C_df_H_d_t, region)

    if type == PROCESS_TYPE_1 or type == PROCESS_TYPE_3:

        """ e_th: ヒートポンプサイクルの理論効率(-) """

        # (20) 中間暖房能力運転時
        e_th_mid_H = calc_e_th_mid_H(type, V_fan_mid_H, q_hs_mid_H, q_hs_rtd_C)
        # (19) 定格暖房能力運転時
        e_th_rtd_H = calc_e_th_rtd_H(type, V_fan_rtd_H, q_hs_rtd_H, q_hs_rtd_C)
        # (17) 日付dの時刻tにおける暖房時
        e_th_H_d_t = calc_e_th_H_d_t(type, Theta_ex_d_t, Theta_hs_in_d_t, Theta_hs_out_d_t, V_hs_supply_d_t, q_hs_rtd_C)

        """ e_r: ヒートポンプサイクルの理論効率に対する熱源機の効率の比(-) """

        if type == PROCESS_TYPE_3:  #コンプレッサ効率特性
            # 日付dの時刻tにおける暖房時
            e_r_H_d_t = get_e_r_H_d_t_2023(q_hs_H_d_t)
        else:
            # (11) 定格暖房能力運転時
            e_r_rtd_H = get_e_r_rtd_H(e_th_rtd_H, q_hs_rtd_H, P_hs_rtd_H, P_fan_rtd_H)
            # (15) 最小暖房能力運転時
            e_r_min_H = get_e_r_min_H(e_r_rtd_H)
            # (13) 中間暖房能力運転時
            e_r_mid_H = get_e_r_mid_H(e_r_rtd_H, e_th_mid_H, q_hs_mid_H, P_hs_mid_H, P_fan_mid_H, EquipmentSpec)
            # (9) 日付dの時刻tにおける暖房時
            e_r_H_d_t = get_e_r_H_d_t(q_hs_H_d_t, q_hs_rtd_H, q_hs_min_H, q_hs_mid_H, e_r_mid_H, e_r_min_H, e_r_rtd_H)

        """ E_E: 日付dの時刻tにおける1時間当たりの暖房時の消費電力量 (kWh/h) """

        # (37) 送風機の付加分（kWh/h）
        E_E_fan_H_d_t = get_E_E_fan_H_d_t(type, P_fan_rtd_H, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_H, q_hs_H_d_t, f_SFP_H)

        # (5) 圧縮機の分
        E_E_comp_H_d_t = get_E_E_comp_H_d_t(
                            q_hs_H_d_t,
                            e_hs_H_d_t = get_e_hs_H_d_t(e_th_H_d_t, e_r_H_d_t))  # (7) 日付dの時刻tにおける暖房時の熱源機の効率(-)
        E_E_H_d_t = E_E_comp_H_d_t + E_E_fan_H_d_t  # (1)

    elif type == PROCESS_TYPE_2 or type == PROCESS_TYPE_4:
        # TODO: f_SFP_H: type2のみのパラメータ type4での使用は怪しい
        # NOTE: ルームエアコンでは V_hs_vent(換気風量) は使用されません

        if type == PROCESS_TYPE_2:
            # NOTE: 別モジュールから同名の関数を利用しています
            E_E_CRAC_H_d_t = \
                pyhees.section4_3.calc_E_E_H_d_t_2024(region,
                                   q_rtd_C, q_rtd_H,  # q[W]
                                   e_rtd_H, dualcompressor_H,
                                   q_hs_H_d_t * 3.6/1000,  # L_H[MJ/h]
                                   q_max_C, q_max_H,  # q[W]
                                   input_C_af_H, climateFile)
            E_E_fan_H_d_t = \
                get_E_E_fan_H_d_t(type, P_rac_fan_rtd_H, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_H,
                                       q_hs_H_d_t,  # q[W]
                                       f_SFP_H)

        elif type == PROCESS_TYPE_4:
            # 『2.2 実験方法と実験条件』より
            # 最大時の給気風量と機器のカタログ公表値(強)の比
            V_ratio1 = (spec.V_inner * 60) / np.max(V_hs_supply_d_t)
            # 室外機/室内機 風量比
            V_ratio2 = spec.V_outer / spec.V_inner

            COP_H_d_t = denchu_2.calc_COP_H_d_t(
                                q_d_t= q_hs_H_d_t / 1000,
                                P_rac_fan_rtd= P_rac_fan_rtd_H / 1000,
                                R= simu_R_H,
                                V_rac_inner_d_t= V_ratio1 * V_hs_supply_d_t,
                                V_rac_outer_d_t= V_ratio2 * V_ratio1 * V_hs_supply_d_t,
                                region= region,
                                Theta_real_inner= Theta_real_inner,
                                RH_real_inner= RH_real_inner,
                                climateFile= climateFile)
            E_E_CRAC_H_d_t = np.divide(q_hs_H_d_t / 1000,  # kW
                                       COP_H_d_t,
                                       out=np.zeros_like(q_hs_H_d_t),
                                       where=COP_H_d_t!=0)  # kWh

            # (37) 送風機の付加分（kWh/h）
            # NOTE: 求めたいのは循環ファンなので P_rac_fan ではなく P_fan を使用する
            E_E_fan_H_d_t = get_E_E_fan_H_d_t(type, P_fan_rtd_H, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_H, q_hs_H_d_t, f_SFP_H)

            df_output_denchuH = pd.DataFrame(index = pd.date_range(
                datetime(2023,1,1,1,0,0), datetime(2024,1,1,0,0,0), freq='h'))

            df_output_denchuH = df_output_denchuH.assign(
                q_hs_H_d_t = q_hs_H_d_t,  # W
                COP_H_d_t = COP_H_d_t,
                E_E_CRAC_H_d_t = E_E_CRAC_H_d_t,  # kW
                E_E_fan_H_d_t = E_E_fan_H_d_t,  # kW
                E_E_H_d_t = E_E_CRAC_H_d_t + E_E_fan_H_d_t  # kW
            )
            df_output_denchuH.to_csv(case_name + constants.version_info() + '_denchu_H_output.csv', encoding='cp932')  # =Shift_JIS

        E_E_H_d_t = E_E_CRAC_H_d_t + E_E_fan_H_d_t

    else:
        raise Exception('暖房設備機器の種類の入力が不正です。')

    return E_E_H_d_t, q_hs_H_d_t, E_E_fan_H_d_t

# TODO: この関数に Q_hat_hs_d_t が使用されないことが妥当でしょうか?
# TODO: 後で名前を統一する(もとになっているpyheesも合わせて)
@constants.jjjexperiment_clone
def get_E_E_C_d_t(
        case_name,
        Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t,  # 空気温度
        V_hs_supply_d_t, V_hs_vent_d_t, V_hs_dsgn_C,      # 風量
        X_hs_out_d_t, X_hs_in_d_t,                        # 絶対湿度
        q_hs_min_C,                                       # 最小冷房時
        q_hs_mid_C, P_hs_mid_C, V_fan_mid_C, P_fan_mid_C,  # 中間冷房時
        q_max_C,                                           # 最大冷房時
        q_hs_rtd_C, P_hs_rtd_C, V_fan_rtd_C, P_fan_rtd_C, q_rtd_C, e_rtd_C, P_rac_fan_rtd_C,  # 定格冷房時
        type, region, dualcompressor_C, EquipmentSpec, input_C_af_C, f_SFP_C, climateFile,  # その他
        simu_R_C=None, spec: Spec=None, Theta_real_inner=None, RH_real_inner=None):  # 電中研モデルのみ使用
    """ (1)
    Args:
        P_fan_rad_C: 定格冷房能力試験 室内側送風機の消費電力 [W]\n
        日付dの時刻tにおける\n
            V_hs_vent_d_t: 熱源機の風量のうちの全般換気分 [m3/h]\n
            V_hs_supply_d_t: 熱源機の風量 [m3/h]\n
            X_hs_in_d_t: 熱源機の入口における絶対湿度 [kg/kg(DA)]\n
            f_SFP_C: ファンの比消費電力 [W/(m3/h)]\n
    Returns:
        日付dの時刻tにおける\n
            E_E_C_d_t: 1時間当たりの 冷房時の消費電力量 [kWh/h]\n
            E_E_fan_C_d_t: 1時間当たりの 冷房時消費電力量の送風機による付加分 [kWh/h]\n
            q_hs_CS_d_t: 1時間当たりの 熱源機の平均冷房 顕熱能力 [W]\n
            q_hs_CL_d_t: 1時間当たりの 熱源機の平均冷房 潜熱能力 [W]\n
    """
    # (4) 日付dの時刻tにおける1時間当たりの熱源機の平均冷房能力(-)
    q_hs_CS_d_t, q_hs_CL_d_t = get_q_hs_C_d_t_2(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, region)

    if type == PROCESS_TYPE_1 or type == PROCESS_TYPE_3:
        """ 顕熱/潜熱 (CS/CL) を使用せずに 全熱負荷(C) を再計算して使用する """

        # (4)
        q_hs_C_d_t = get_q_hs_C_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, region)
        _logger.NDdebug("q_hs_C_d_t", q_hs_C_d_t)

        """ e_th: ヒートポンプサイクルの理論効率(-) """

        # (22) 中間冷房能力運転時
        e_th_mid_C = calc_e_th_mid_C(type, V_fan_mid_C, q_hs_mid_C, q_hs_rtd_C)
        # (21) 定格冷房能力運転時
        e_th_rtd_C = calc_e_th_rtd_C(type, V_fan_rtd_C, q_hs_rtd_C)
        # (18) 日付dの時刻tにおける暖房時
        e_th_C_d_t = calc_e_th_C_d_t(type, Theta_ex_d_t, Theta_hs_in_d_t, X_hs_in_d_t, Theta_hs_out_d_t, V_hs_supply_d_t, q_hs_rtd_C)

        """ e_r: ヒートポンプサイクルの理論効率に対する熱源機の効率の比(-) """

        if type == PROCESS_TYPE_1:
            # (11) 定格冷房能力運転時
            e_r_rtd_C = get_e_r_rtd_C(e_th_rtd_C, q_hs_rtd_C, P_hs_rtd_C, P_fan_rtd_C)
            # (15) 最小冷房能力運転時
            e_r_min_C = get_e_r_min_C(e_r_rtd_C)
            # (13) 定格冷房能力運転時
            e_r_mid_C = get_e_r_mid_C(e_r_rtd_C, e_th_mid_C, q_hs_mid_C, P_hs_mid_C, P_fan_mid_C, EquipmentSpec)
            # (9) 日付dの時刻tにおける冷房時
            e_r_C_d_t = get_e_r_C_d_t(q_hs_C_d_t, q_hs_rtd_C, q_hs_min_C, q_hs_mid_C, e_r_mid_C, e_r_min_C, e_r_rtd_C)

        elif type == PROCESS_TYPE_3:  #コンプレッサ効率特性
            # TODO: 潜熱評価モデルが 潜熱(q_hs_CL) ではなく 全熱(q_hs_C) を使用してOKか確認
            e_r_C_d_t = get_e_r_C_d_t_2023(q_hs_C_d_t)  # 日付dの時刻tにおける冷房時

        """ E_E: 日付dの時刻tにおける1時間当たりの冷房時の消費電力量 (kWh/h) """

        # (38) 送風機の付加分 (kWh/h)
        E_E_fan_C_d_t = get_E_E_fan_C_d_t(type, P_fan_rtd_C, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_C, q_hs_C_d_t, f_SFP_C)

        # (6) 圧縮機の分
        E_E_comp_C_d_t = get_E_E_comp_C_d_t(
                            q_hs_C_d_t,
                            e_hs_C_d_t = get_e_hs_C_d_t(e_th_C_d_t, e_r_C_d_t))  # (8)

        _logger.NDdebug("E_E_comp_C_d_t", E_E_comp_C_d_t)
        _logger.NDdebug("E_E_fan_C_d_t", E_E_fan_C_d_t)
        E_E_C_d_t = E_E_comp_C_d_t + E_E_fan_C_d_t  # (2)

    elif type == PROCESS_TYPE_2 or type == PROCESS_TYPE_4:
        """ 顕熱/潜熱 (CS/CL) を使用する """
        # NOTE: ルームエアコンでは V_hs_vent(換気風量) は使用されません

        if type == PROCESS_TYPE_2:
            # NOTE: 別モジュールから同名の関数を利用しています
            E_E_CRAC_C_d_t = \
                pyhees.section4_3.calc_E_E_C_d_t_2024(region, q_rtd_C,  # q[W]
                                   e_rtd_C, dualcompressor_C,
                                   q_hs_CS_d_t * 3.6/1000, q_hs_CL_d_t * 3.6/1000,  # L_H[MJ/h]
                                   q_max_C, input_C_af_C, climateFile)
            # (38) 送風機の付加分 (kWh/h)
            E_E_fan_C_d_t = \
                get_E_E_fan_C_d_t(type, P_rac_fan_rtd_C,
                                       V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_C,
                                       (q_hs_CS_d_t + q_hs_CL_d_t),  # q[W]
                                       f_SFP_C)

        elif type == PROCESS_TYPE_4:
            # 『2.2 実験方法と実験条件』より
            # 最大時の給気風量と機器のカタログ公表値(強)の比
            V_ratio1 = (spec.V_inner * 60) / np.max(V_hs_supply_d_t)
            # 室外機/室内機 風量比
            V_ratio2 = spec.V_outer / spec.V_inner

            q_hs_C_d_t = q_hs_CS_d_t + q_hs_CL_d_t

            # FIXME: COPが大きすぎる問題があります
            COP_C_d_t = denchu_2.calc_COP_C_d_t(
                            q_d_t= q_hs_C_d_t / 1000,
                            P_rac_fan_rtd= P_rac_fan_rtd_C / 1000,
                            R= simu_R_C,
                            V_rac_inner_d_t= V_ratio1 * V_hs_supply_d_t,
                            V_rac_outer_d_t= V_ratio2 * V_ratio1 * V_hs_supply_d_t,
                            region= region,
                            Theta_real_inner= Theta_real_inner,
                            RH_real_inner= RH_real_inner,
                            climateFile= climateFile)
            E_E_CRAC_C_d_t = np.divide(q_hs_C_d_t / 1000,  # kW
                                COP_C_d_t,
                                out=np.zeros_like(q_hs_C_d_t),
                                where=COP_C_d_t!=0)  # kWh

            # (38) 送風機の付加分 (kWh/h)
            E_E_fan_C_d_t = get_E_E_fan_C_d_t(type, P_fan_rtd_C, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_C, q_hs_C_d_t, f_SFP_C)

            df_output_denchuC = pd.DataFrame(index = pd.date_range(
                datetime(2023,1,1,1,0,0), datetime(2024,1,1,0,0,0), freq='h'))

            df_output_denchuC = df_output_denchuC.assign(
                q_hs_C_d_t = q_hs_C_d_t,  # W
                COP_C_d_t = COP_C_d_t,
                E_E_CRAC_C_d_t = E_E_CRAC_C_d_t,  # kW
                E_E_fan_C_d_t = E_E_fan_C_d_t,  # kW
                E_E_C_d_t = E_E_CRAC_C_d_t + E_E_fan_C_d_t  # kW
            )
            df_output_denchuC.to_csv(case_name + constants.version_info() + '_denchu_C_output.csv', encoding='cp932')  # =Shift_JIS

        _logger.NDdebug("E_E_CRAC_C_d_t", E_E_CRAC_C_d_t)
        _logger.NDdebug("E_E_fan_C_d_t", E_E_fan_C_d_t)
        E_E_C_d_t = E_E_CRAC_C_d_t + E_E_fan_C_d_t  # (2)

    else:
        raise Exception('冷房設備機器の種類の入力が不正です。')

    return E_E_C_d_t, E_E_fan_C_d_t, q_hs_CS_d_t, q_hs_CL_d_t
