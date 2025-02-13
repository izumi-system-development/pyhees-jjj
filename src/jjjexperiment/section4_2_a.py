import numpy as np
import pandas as pd
from datetime import datetime
from nptyping import NDArray, Shape, Float64

import pyhees.section4_2_a as dc_a
import pyhees.section4_3

# JJJ
from jjjexperiment.denchu_1 import Spec
from jjjexperiment.logger import LimitedLoggerAdapter as _logger  # デバッグ用ロガー
import jjjexperiment.constants as constants
from jjjexperiment.constants import PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_3, PROCESS_TYPE_4
import jjjexperiment.denchu_2 as denchu_2
from jjjexperiment.options import *
import jjjexperiment.ac_min_volume_input as jjj_V_min_input

def calc_E_E_fan_H_d_t(
        type, region, case_name,
        Theta_hs_out_d_t, Theta_hs_in_d_t,  # 空気温度
        V_hs_supply_d_t, V_hs_vent_d_t, V_hs_dsgn_H,  # 風量
        C_df_H_d_t,  # 暖房出力補正係数
        P_rac_fan_rtd_H, P_fan_rtd_H,  # 定格暖房時
        f_SFP_H  # その他
    ) -> NDArray[Shape['8760'], Float64]:
    """ (37)改 E_E_fan_H_d_t
    """
    # (3) 日付dの時刻tにおける1時間当たりの熱源機の平均暖房能力(W)
    q_hs_H_d_t = dc_a.get_q_hs_H_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, V_hs_supply_d_t, C_df_H_d_t, region)

    # (37) 送風機の付加分 [kWh/h]
    if constants.input_V_hs_min == 最低風量直接入力.入力する.value:
        E_E_fan_H_d_t \
            = jjj_V_min_input.get_E_E_fan_H_d_t(
                P_rac_fan_rtd_H, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_H)

    elif constants.input_V_hs_min == 最低風量直接入力.入力しない.value:
        # デフォルト条件では V_hs_vent_d_t は既存式(35)のまま
        E_E_fan_H_d_t \
            = dc_a.get_E_E_fan_H_d_t(type,
                    # NOTE: ルームエアコンファン(P_rac_fan) / 循環ファン(P_fan) 切替
                    P_rac_fan_rtd_H if type == PROCESS_TYPE_2 else P_fan_rtd_H,
                    V_hs_vent_d_t,
                    V_hs_supply_d_t,
                    V_hs_dsgn_H,
                    q_hs_H_d_t,  # [W]
                    f_SFP_H)
    else:
        raise ValueError(constants.input_V_hs_min)

    _logger.NDdebug("E_E_fan_H_d_t", E_E_fan_H_d_t)
    return E_E_fan_H_d_t, q_hs_H_d_t

def calc_E_E_fan_C_d_t(
        type, region, case_name,
        Theta_hs_out_d_t, Theta_hs_in_d_t,
        V_hs_supply_d_t, V_hs_vent_d_t, V_hs_dsgn_C,  # 風量
        X_hs_out_d_t, X_hs_in_d_t,  # 絶対湿度
        P_rac_fan_rtd_C, P_fan_rtd_C,  # 定格暖房時
        f_SFP_C  # その他
    ) -> NDArray[Shape['8760'], Float64]:
    """ (38)改 E_E_fan_C_d_t
    """
    # (4) 日付dの時刻tにおける1時間当たりの熱源機の平均冷房能力(-)
    q_hs_CS_d_t, q_hs_CL_d_t = dc_a.get_q_hs_C_d_t_2(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, region)

    # (38) 送風機の付加分 [kWh/h]
    if constants.input_V_hs_min == 最低風量直接入力.入力する.value:
        E_E_fan_C_d_t \
            = jjj_V_min_input.get_E_E_fan_C_d_t(
                P_rac_fan_rtd_C, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_C)

    elif constants.input_V_hs_min == 最低風量直接入力.入力しない.value:
        if (type == PROCESS_TYPE_1 or type == PROCESS_TYPE_3):
            # (4) 潜熱/顕熱を使用せずに全熱負荷を再計算する
            q_hs_C_d_t = dc_a.get_q_hs_C_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, region)
        else:
            # 潜熱/顕熱を使用する
            q_hs_C_d_t = q_hs_CS_d_t + q_hs_CL_d_t

        E_E_fan_C_d_t \
            = dc_a.get_E_E_fan_C_d_t(type,
                    # NOTE: ルームエアコンファン(P_rac_fan) / 循環ファン(P_fan) 切替
                    P_rac_fan_rtd_C if type == PROCESS_TYPE_2 else P_fan_rtd_C,
                    V_hs_vent_d_t,
                    V_hs_supply_d_t,
                    V_hs_dsgn_C,
                    q_hs_C_d_t,  # [W]
                    f_SFP_C)
    else:
        raise ValueError(constants.input_V_hs_min)

    _logger.NDdebug("E_E_fan_C_d_t", E_E_fan_C_d_t)
    return E_E_fan_C_d_t, q_hs_CS_d_t, q_hs_CL_d_t

def calc_E_E_H_d_t_type1_and_type3(
        type: str,
        E_E_fan_H_d_t: NDArray[Shape['8760'], Float64],
        q_hs_H_d_t: NDArray[Shape['8760'], Float64],
        Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t,  # 空気温度
        V_hs_supply_d_t,  # 風量
        q_hs_rtd_C,  # 定格冷房能力※
        q_hs_min_H,  # 最小冷房時
        q_hs_mid_H, P_hs_mid_H, V_fan_mid_H, P_fan_mid_H,  # 中間冷房時
        q_hs_rtd_H, P_fan_rtd_H, V_fan_rtd_H, P_hs_rtd_H,  # 定格冷房時
        EquipmentSpec,  # その他
    ) -> NDArray[Shape['8760'], Float64]:
    """ (1)改 E_E_H_d_t
    """
    assert type == PROCESS_TYPE_1 or type == PROCESS_TYPE_3, "type1,3 専用ロジック"

    """ e_th: ヒートポンプサイクルの理論効率(-) """
    # (20) 中間暖房能力運転時
    e_th_mid_H = dc_a.calc_e_th_mid_H(type, V_fan_mid_H, q_hs_mid_H, q_hs_rtd_C)
    # (19) 定格暖房能力運転時
    e_th_rtd_H = dc_a.calc_e_th_rtd_H(type, V_fan_rtd_H, q_hs_rtd_H, q_hs_rtd_C)
    # (17) 日付dの時刻tにおける暖房時
    e_th_H_d_t = dc_a.calc_e_th_H_d_t(type, Theta_ex_d_t, Theta_hs_in_d_t, Theta_hs_out_d_t, V_hs_supply_d_t, q_hs_rtd_C)

    """ e_r: ヒートポンプサイクルの理論効率に対する熱源機の効率の比(-) """
    if type == PROCESS_TYPE_3:  #コンプレッサ効率特性
        # 日付dの時刻tにおける暖房時
        e_r_H_d_t = dc_a.get_e_r_H_d_t_2023(q_hs_H_d_t)
    else:
        # (11) 定格暖房能力運転時
        e_r_rtd_H = dc_a.get_e_r_rtd_H(e_th_rtd_H, q_hs_rtd_H, P_hs_rtd_H, P_fan_rtd_H)
        # (15) 最小暖房能力運転時
        e_r_min_H = dc_a.get_e_r_min_H(e_r_rtd_H)
        # (13) 中間暖房能力運転時
        e_r_mid_H = dc_a.get_e_r_mid_H(e_r_rtd_H, e_th_mid_H, q_hs_mid_H, P_hs_mid_H, P_fan_mid_H, EquipmentSpec)
        # (9) 日付dの時刻tにおける暖房時
        e_r_H_d_t = dc_a.get_e_r_H_d_t(q_hs_H_d_t, q_hs_rtd_H, q_hs_min_H, q_hs_mid_H, e_r_mid_H, e_r_min_H, e_r_rtd_H)

    """ E_E: 日付dの時刻tにおける1時間当たりの暖房時の消費電力量 (kWh/h) """
    # (5) 圧縮機の分
    E_E_comp_H_d_t = dc_a.get_E_E_comp_H_d_t(
                        q_hs_H_d_t,
                        e_hs_H_d_t = dc_a.get_e_hs_H_d_t(e_th_H_d_t, e_r_H_d_t))  # (7) 日付dの時刻tにおける暖房時の熱源機の効率(-)

    E_E_H_d_t = E_E_comp_H_d_t + E_E_fan_H_d_t  # (1)
    return E_E_H_d_t

def calc_E_E_H_d_t_type2(
        type: str,
        region: int,
        climateFile,
        E_E_fan_H_d_t: NDArray[Shape['8760'], Float64],
        q_hs_H_d_t: NDArray[Shape['8760'], Float64],
        e_rtd_H: float,
        q_rtd_H: float,
        q_rtd_C: float,
        q_max_H: float,
        q_max_C: float,
        input_C_af_H: float,
        dualcompressor_H: bool,
    ) -> NDArray[Shape['8760'], Float64]:
    """ (1)改 E_E_H_d_t
    """
    assert type == PROCESS_TYPE_2, "type2 専用ロジック"
    # TODO: f_SFP_H: type2のみのパラメータ type4での使用は怪しい
    # NOTE: 別モジュールから同名の関数を利用しています
    E_E_CRAC_H_d_t = \
        pyhees.section4_3.calc_E_E_H_d_t_2024(region,
                           q_rtd_C, q_rtd_H,  # q[W]
                           e_rtd_H, dualcompressor_H,
                           q_hs_H_d_t * 3.6/1000,  # L_H[MJ/h]
                           q_max_C, q_max_H,  # q[W]
                           input_C_af_H, climateFile)

    E_E_H_d_t = E_E_fan_H_d_t + E_E_CRAC_H_d_t
    return E_E_H_d_t

def calc_E_E_H_d_t_type4(
        case_name: str,
        type: str,
        region: int,
        climateFile,
        E_E_fan_H_d_t: NDArray[Shape['8760'], Float64],
        q_hs_H_d_t: NDArray[Shape['8760'], Float64],
        V_hs_supply_d_t: NDArray[Shape['8760'], Float64],
        P_rac_fan_rtd_H: float,
        simu_R_H,
        spec: Spec,
        Theta_real_inner,
        RH_real_inner,
    ) -> NDArray[Shape['8760'], Float64]:
    """ (1)改 E_E_H_d_t
    """
    assert type == PROCESS_TYPE_4, "type4 専用ロジック"
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

    # 電中研モデル調査用
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

    E_E_H_d_t = E_E_fan_H_d_t + E_E_CRAC_H_d_t
    return E_E_H_d_t

def calc_E_E_C_d_t_type1_and_type3(
        type, region,
        E_E_fan_C_d_t: NDArray[Shape['8760'], Float64],
        Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t,  # 空気温度
        V_hs_supply_d_t,  # 風量
        X_hs_out_d_t, X_hs_in_d_t,  # 絶対湿度
        q_hs_min_C,  # 最小冷房時
        q_hs_mid_C, P_hs_mid_C, V_fan_mid_C, P_fan_mid_C,  # 中間冷房時
        q_hs_rtd_C, P_fan_rtd_C, V_fan_rtd_C, P_hs_rtd_C,  # 定格冷房時
        EquipmentSpec,  # その他
    ) -> NDArray[Shape['8760'], Float64]:
    """ (2)改 E_E_C_d_t
    """
    assert type == PROCESS_TYPE_1 or type == PROCESS_TYPE_3, "type1,3 専用ロジック"

    # (4) 潜熱/顕熱を使用せずに全熱負荷を再計算する
    q_hs_C_d_t = dc_a.get_q_hs_C_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, region)

    """ e_th: ヒートポンプサイクルの理論効率(-) """
    # (22) 中間冷房能力運転時
    e_th_mid_C = dc_a.calc_e_th_mid_C(type, V_fan_mid_C, q_hs_mid_C, q_hs_rtd_C)
    # (21) 定格冷房能力運転時
    e_th_rtd_C = dc_a.calc_e_th_rtd_C(type, V_fan_rtd_C, q_hs_rtd_C)
    # (18) 日付dの時刻tにおける暖房時
    e_th_C_d_t = dc_a.calc_e_th_C_d_t(type, Theta_ex_d_t, Theta_hs_in_d_t, X_hs_in_d_t, Theta_hs_out_d_t, V_hs_supply_d_t, q_hs_rtd_C)

    """ e_r: ヒートポンプサイクルの理論効率に対する熱源機の効率の比(-) """
    if type == PROCESS_TYPE_1:
        # (11) 定格冷房能力運転時
        e_r_rtd_C = dc_a.get_e_r_rtd_C(e_th_rtd_C, q_hs_rtd_C, P_hs_rtd_C, P_fan_rtd_C)
        # (15) 最小冷房能力運転時
        e_r_min_C = dc_a.get_e_r_min_C(e_r_rtd_C)
        # (13) 定格冷房能力運転時
        e_r_mid_C = dc_a.get_e_r_mid_C(e_r_rtd_C, e_th_mid_C, q_hs_mid_C, P_hs_mid_C, P_fan_mid_C, EquipmentSpec)
        # (9) 日付dの時刻tにおける冷房時
        e_r_C_d_t = dc_a.get_e_r_C_d_t(q_hs_C_d_t, q_hs_rtd_C, q_hs_min_C, q_hs_mid_C, e_r_mid_C, e_r_min_C, e_r_rtd_C)
    elif type == PROCESS_TYPE_3:  #コンプレッサ効率特性
        # TODO: 潜熱評価モデルが 潜熱(q_hs_CL) ではなく 全熱(q_hs_C) を使用してOKか確認
        e_r_C_d_t = dc_a.get_e_r_C_d_t_2023(q_hs_C_d_t)  # 日付dの時刻tにおける冷房時
    else:
        raise Exception('冷房設備機器の種類の入力が不正です。')

    """ E_E: 日付dの時刻tにおける1時間当たりの冷房時の消費電力量 (kWh/h) """
    # (6) 圧縮機の分
    E_E_comp_C_d_t = dc_a.get_E_E_comp_C_d_t(
                        q_hs_C_d_t,
                        e_hs_C_d_t = dc_a.get_e_hs_C_d_t(e_th_C_d_t, e_r_C_d_t))  # (8)
    _logger.NDdebug("E_E_comp_C_d_t", E_E_comp_C_d_t)

    E_E_C_d_t = E_E_comp_C_d_t + E_E_fan_C_d_t  # (2)
    return E_E_C_d_t

def calc_E_E_C_d_t_type2(
        type: str,
        region: int,
        climateFile,
        E_E_fan_C_d_t: NDArray[Shape['8760'], Float64],
        q_hs_CS_d_t: NDArray[Shape['8760'], Float64],
        q_hs_CL_d_t: NDArray[Shape['8760'], Float64],
        e_rtd_C: float,
        q_rtd_C: float,
        q_max_C: float,
        input_C_af_C: float,
        dualcompressor_C: bool,
    ) -> NDArray[Shape['8760'], Float64]:
    """ (2)改 E_E_C_d_t
    """
    assert type == PROCESS_TYPE_2, "type2 専用ロジック"

    """ 顕熱/潜熱 (CS/CL) を使用する """
    # NOTE: 別モジュールから同名の関数を利用しています
    E_E_CRAC_C_d_t = \
        pyhees.section4_3.calc_E_E_C_d_t_2024(region, q_rtd_C,  # q[W]
                           e_rtd_C, dualcompressor_C,
                           q_hs_CS_d_t * 3.6/1000, q_hs_CL_d_t * 3.6/1000,  # L_H[MJ/h]
                           q_max_C, input_C_af_C, climateFile)

    _logger.NDdebug("E_E_CRAC_C_d_t", E_E_CRAC_C_d_t)
    E_E_C_d_t = E_E_CRAC_C_d_t + E_E_fan_C_d_t  # (2)
    return E_E_C_d_t

def calc_E_E_C_d_t_type4(
        case_name: str,
        type: str,
        region: int,
        climateFile,
        E_E_fan_C_d_t: NDArray[Shape['8760'], Float64],
        q_hs_C_d_t: NDArray[Shape['8760'], Float64],  # NOTE: CS/CL 足せばよい
        V_hs_supply_d_t: NDArray[Shape['8760'], Float64],
        P_rac_fan_rtd_C: float,
        simu_R_C,
        spec: Spec,
        Theta_real_inner,
        RH_real_inner,
    ) -> NDArray[Shape['8760'], Float64]:
    """ (2)改 E_E_C_d_t
    """
    assert type == PROCESS_TYPE_4, "type4 専用ロジック"

    # 『2.2 実験方法と実験条件』より
    # 最大時の給気風量と機器のカタログ公表値(強)の比
    V_ratio1 = (spec.V_inner * 60) / np.max(V_hs_supply_d_t)
    # 室外機/室内機 風量比
    V_ratio2 = spec.V_outer / spec.V_inner

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

    # 電中研モデル調査用
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
    E_E_C_d_t = E_E_CRAC_C_d_t + E_E_fan_C_d_t  # (2)
    return E_E_C_d_t
