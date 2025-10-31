import json
import numpy as np
import pandas as pd
from datetime import datetime

from pyhees.section2_1_b import get_f_prim

from pyhees.section4_1 import calc_heating_load, calc_cooling_load, get_virtual_heating_devices, get_alpha_UT_H_A
from pyhees.section4_1_a import calc_heating_mode

# ダクト式セントラル空調機
import pyhees.section4_2_a as dc_a
import pyhees.section4_2_b as dc_spec

# 床下
import pyhees.section3_1 as ld
from pyhees.section3_2 import calc_r_env, get_Q_dash, get_mu_H, get_mu_C

""" オーバーライドロジック """

import jjjexperiment.section4_2 as jjj_dc
import jjjexperiment.section4_2_a as jjj_dc_a

""" 独自ロジック """

# 電中研モデルロジック
import jjjexperiment.denchu_1
import jjjexperiment.denchu_2

import jjjexperiment.input
import jjjexperiment.constants as jjj_consts
from jjjexperiment.app_config import *
from jjjexperiment.constants import PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_3, PROCESS_TYPE_4
from jjjexperiment.result import *
from jjjexperiment.logger import LimitedLoggerAdapter as _logger  # デバッグ用ロガー
from jjjexperiment.options import *
from jjjexperiment.common import *
import jjjexperiment.inputs as jjj_ipt

# [F25-01] 最低風量の直接入力
import jjjexperiment.ac_min_volume_input as jjj_V_min_input

def calc(input_data: dict, test_mode=False):
    case_name   = input_data['case_name']
    climateFile = input_data['climateFile']
    loadFile    = input_data['loadFile']

    with open(case_name + jjj_consts.version_info() + '_input.json', 'w') as f:
        json.dump(input_data, f, indent=4)

    injector.get(AppConfig).update(input_data)

    jjj_consts.set_constants(input_data)
    type, tatekata, A_A, A_MR, A_OR, region, sol_region = jjjexperiment.input.get_basic(input_data)
    ENV, NV_MR, NV_OR, TS, r_A_ufvnt, underfloor_insulation, underfloor_air_conditioning_air_supply, hs_CAV = jjjexperiment.input.get_env(input_data)
    mode_H, H_A, H_MR, H_OR, H_HS = jjjexperiment.input.get_heating(input_data, region, A_A)
    mode_C, C_A, C_MR, C_OR = jjjexperiment.input.get_cooling(input_data, region, A_A)
    q_rtd_C, q_rtd_H, q_max_C, q_max_H, e_rtd_C, e_rtd_H, dualcompressor_C, dualcompressor_H, input_C_af_C, input_C_af_H = jjjexperiment.input.get_CRAC_spec(input_data)

    print("q_rtd_C, q_rtd_H, q_max_C, q_max_H, e_rtd_C, e_rtd_H")
    print(q_rtd_C, q_rtd_H, q_max_C, q_max_H, e_rtd_C, e_rtd_H)

    _logger.info(f"q_rtd_C [w]: {q_rtd_C}")  # q[W] 送風機の単位[W]と同じ
    _logger.info(f"q_max_C [w]: {q_max_C}")
    _logger.info(f"e_rtd_C [-]: {e_rtd_C}")
    _logger.info(f"q_rtd_H [w]: {q_rtd_H}")
    _logger.info(f"q_max_H [w]: {q_max_H}")
    _logger.info(f"e_rtd_H [-]: {e_rtd_H}")

    # 熱交換型換気の取得
    HEX = jjjexperiment.input.get_heatexchangeventilation(input_data)

    # 太陽熱利用の取得
    SHC = jjjexperiment.input.get_solarheat()

    # 床面積の合計に対する外皮の部位の面積の合計の比
    r_env = calc_r_env(
        method='当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法',
        A_env=ENV['A_env'],
        A_A=A_A
    )

    # 熱損失係数（換気による熱損失を含まない）
    Q_dash = get_Q_dash(ENV['U_A'], r_env)
    # 熱損失係数
    Q = ld.get_Q(Q_dash)

    # 日射取得係数の取得
    mu_H = get_mu_H(ENV['eta_A_H'], r_env)
    mu_C = get_mu_C(ENV['eta_A_C'], r_env)

    # 実質的な暖房機器の仕様を取得
    spec_MR, spec_OR = get_virtual_heating_devices(region, H_MR, H_OR)

    # 暖房方式及び運転方法の区分
    mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)

    # 空調空気を床下を通して給気する場合（YUCACO）の「床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)」
    YUCACO_r_A_ufvnt = (8.28+16.56+21.53) / (9.52+1.24+3.31+3.31+1.66+8.28+16.56+21.53)

    ##### 暖房負荷の取得（MJ/h）

    L_H_d_t_i: np.ndarray
    """暖房負荷 [MJ/h]"""

    # L_dash_H_R_d_t_i, L_dash_CS_R_d_t_iは負荷ファイルから読み取れないため自動計算する。
    # 読み込んだ負荷と整合性が取れないため、正しい実装ではない。
    L_H_d_t_i, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i  = calc_heating_load(region, sol_region, A_A, A_MR, A_OR, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt,
                                    HEX, underfloor_insulation, mode_H, mode_C, spec_MR, spec_OR, mode_MR, mode_OR, SHC)
    if loadFile != '-':
        load = pd.read_csv(loadFile, nrows=24 * 365)
        L_H_d_t_i = load.iloc[::,:12].T.values

    L_H_d_t: np.ndarray = np.sum(L_H_d_t_i, axis=0)
    """暖房負荷の全区画合計 [MJ/h]"""

    ##### 冷房負荷の取得（MJ/h）
    L_CS_d_t_i: np.ndarray
    """冷房顕熱負荷 [MJ/h]"""
    L_CL_d_t_i: np.ndarray
    """冷房潜熱負荷 [MJ/h]"""

    if loadFile == '-':
        L_CS_d_t_i, L_CL_d_t_i = calc_cooling_load(region, A_A, A_MR, A_OR, Q, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt,
                                                underfloor_insulation, mode_C, mode_H, mode_MR, mode_OR, TS, HEX)
    else:
        load = pd.read_csv(loadFile, nrows=24 * 365)
        L_CS_d_t_i = load.iloc[::,12:24].T.values
        L_CL_d_t_i = load.iloc[::,24:].T.values

    L_CS_d_t: np.ndarray = np.sum(L_CS_d_t_i, axis=0)
    """冷房顕熱負荷の全区画合計 [MJ/h]"""
    L_CL_d_t: np.ndarray = np.sum(L_CL_d_t_i, axis=0)
    """冷房潜熱負荷の全区画合計 [MJ/h]"""

    ##### 暖房消費電力の計算（kWh/h）

    def get_V_hs_dsgn_H(H_A: dict, q_rtd_H: float):
        if H_A['type']==PROCESS_TYPE_1 or H_A['type']==PROCESS_TYPE_3:
            V_fan_rtd_H = H_A['V_fan_rtd_H']
        elif H_A['type']== PROCESS_TYPE_2 or H_A['type']==PROCESS_TYPE_4:
            V_fan_rtd_H = dc_spec.get_V_fan_rtd_H(q_rtd_H)
        else:
            raise Exception("暖房方式が不正です。")

        return dc_spec.get_V_fan_dsgn_H(V_fan_rtd_H)

    V_hs_dsgn_H = H_A['V_hs_dsgn_H'] if 'V_hs_dsgn_H' in H_A else get_V_hs_dsgn_H(H_A, q_rtd_H)
    """ 暖房時の送風機の設計風量[m3/h] """
    V_hs_dsgn_C: float = None  # NOTE: 暖房負荷計算時は空
    """ 冷房時の送風機の設計風量[m3/h] """

    Q_UT_H_d_t_i: np.ndarray
    """暖房設備機器等の未処理暖房負荷(MJ/h)"""

    def arr_summary(arr: np.ndarray):
        return {
            "MAX  ": max(arr),
            "ZEROS": arr.size - np.count_nonzero(arr),
            "AVG  ": np.average(arr[np.nonzero(arr)])
        }

    calc_Q_UT_A_input = {
        'case_name': case_name,
        'A_A': A_A,
        'A_MR': A_MR,
        'A_OR': A_OR,
        'r_env': r_env,
        'mu_H': mu_H,
        'mu_C': mu_C,
        'q_hs_rtd_H': H_A['q_hs_rtd_H'],
        'q_hs_rtd_C': None,
        'q_rtd_H': q_rtd_H,
        'q_rtd_C': q_rtd_C,
        'q_max_H': q_max_H,
        'q_max_C': q_max_C,
        'V_hs_dsgn_H': V_hs_dsgn_H,
        'V_hs_dsgn_C': V_hs_dsgn_C,
        'Q': Q,
        'VAV': H_A['VAV'],
        'general_ventilation': H_A['general_ventilation'],
        'hs_CAV': hs_CAV,
        'duct_insulation': H_A['duct_insulation'],
        'region': region,
        'L_H_d_t_1': arr_summary(L_H_d_t_i[0]),
        'L_H_d_t_2': arr_summary(L_H_d_t_i[1]),
        'L_H_d_t_3': arr_summary(L_H_d_t_i[2]),
        'L_H_d_t_4': arr_summary(L_H_d_t_i[3]),
        'L_H_d_t_5': arr_summary(L_H_d_t_i[4]),
        'L_CS_d_t_1': arr_summary(L_CS_d_t_i[0]),
        'L_CS_d_t_2': arr_summary(L_CS_d_t_i[1]),
        'L_CS_d_t_3': arr_summary(L_CS_d_t_i[2]),
        'L_CS_d_t_4': arr_summary(L_CS_d_t_i[3]),
        'L_CS_d_t_5': arr_summary(L_CS_d_t_i[4]),
        'L_CL_d_t_1': arr_summary(L_CL_d_t_i[0]),
        'L_CL_d_t_2': arr_summary(L_CL_d_t_i[1]),
        'L_CL_d_t_3': arr_summary(L_CL_d_t_i[2]),
        'L_CL_d_t_4': arr_summary(L_CL_d_t_i[3]),
        'L_CL_d_t_5': arr_summary(L_CL_d_t_i[4]),
        'L_dash_H_R_d_t_1': arr_summary(L_dash_H_R_d_t_i[0]),
        'L_dash_H_R_d_t_2': arr_summary(L_dash_H_R_d_t_i[1]),
        'L_dash_H_R_d_t_3': arr_summary(L_dash_H_R_d_t_i[2]),
        'L_dash_H_R_d_t_4': arr_summary(L_dash_H_R_d_t_i[3]),
        'L_dash_H_R_d_t_5': arr_summary(L_dash_H_R_d_t_i[4]),
        'L_dash_CS_R_d_t_1': arr_summary(L_dash_CS_R_d_t_i[0]),
        'L_dash_CS_R_d_t_2': arr_summary(L_dash_CS_R_d_t_i[1]),
        'L_dash_CS_R_d_t_3': arr_summary(L_dash_CS_R_d_t_i[2]),
        'L_dash_CS_R_d_t_4': arr_summary(L_dash_CS_R_d_t_i[3]),
        'L_dash_CS_R_d_t_5': arr_summary(L_dash_CS_R_d_t_i[4]),
        'type': H_A['type'],
        'input_C_af_H': input_C_af_H,
        'input_C_af_C': input_C_af_C,
        'r_A_ufvnt': r_A_ufvnt,
        'underfloor_insulation': underfloor_insulation,
        'underfloor_air_conditioning_air_supply': underfloor_air_conditioning_air_supply,
        'YUCACO_r_A_ufvnt': YUCACO_r_A_ufvnt,
        'climateFile': climateFile
    }
    if test_mode and False:
        # 調査用
        with open(case_name + jjj_consts.version_info() + '_calc_Q_UT_A_input.json', 'w') as json_file:
            json.dump(calc_Q_UT_A_input, json_file, indent=4, ensure_ascii=False)
    else:
        pass

    _, Q_UT_H_d_t_i, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t, _, _, V_hs_supply_d_t, V_hs_vent_d_t, C_df_H_d_t, \
        = jjj_dc.calc_Q_UT_A(case_name, A_A, A_MR, A_OR, r_env, mu_H, mu_C,
            H_A['q_hs_rtd_H'], None,  # 暖房時 Q,hs,rtd,C 初期化しない
            q_rtd_H, q_rtd_C, q_max_H, q_max_C, V_hs_dsgn_H, V_hs_dsgn_C, Q, H_A['VAV'], H_A['general_ventilation'], hs_CAV,
            H_A['duct_insulation'], region, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i,
            H_A['type'], input_C_af_H, input_C_af_C,
            r_A_ufvnt, underfloor_insulation, underfloor_air_conditioning_air_supply, YUCACO_r_A_ufvnt, climateFile)
    _logger.NDdebug("V_hs_supply_d_t", V_hs_supply_d_t)
    _logger.NDdebug("V_hs_vent_d_t", V_hs_vent_d_t)

    if H_A['type'] == PROCESS_TYPE_4:
        spec, cdtn, T_real, RH_real = jjjexperiment.input.get_rac_catalog_spec(input_data, TH_FC=True)
        R2, R1, R0, P_rac_fan_rtd_H = jjjexperiment.denchu_1.calc_R_and_Pc_H(spec, cdtn)
        P_rac_fan_rtd_H = 1000 * P_rac_fan_rtd_H  # kW -> W
        simu_R_H = jjjexperiment.denchu_2.simu_R(R2, R1, R0)

        """ 電柱研モデルのモデリング定数の確認のためのCSV出力 """
        df_denchu_consts = jjjexperiment.denchu_1 \
            .get_DataFrame_denchu_modeling_consts(spec, cdtn, R2, R1, R0, T_real, RH_real, P_rac_fan_rtd_H)
        df_denchu_consts.to_csv(case_name + jjj_consts.version_info() + '_denchu_consts_H_output.csv', encoding='cp932')

        del cdtn, R2, R1, R0  # NOTE: 以降不要
    else:
        P_rac_fan_rtd_H = V_hs_dsgn_H * H_A['f_SFP_H']
    """定格暖房能力運転時の送風機の消費電力(W)"""
    _logger.info(f"P_rac_fan_rtd_H [W]: {P_rac_fan_rtd_H}")

    # (3) 日付dの時刻tにおける1時間当たりの熱源機の平均暖房能力(W)
    q_hs_H_d_t = \
        dc_a.get_q_hs_H_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, V_hs_supply_d_t, C_df_H_d_t, region)
    # NOTE: 消費電力量計算に広く使用されており、広いスコープで定義してよいことを確認済

    climate = jjj_ipt.ClimateEntity(region)
    HCM = climate.get_HCM_d_t()

    E_E_fan_H_d_t: Array8760
    # NOTE: 潜熱評価モデルはベース式が異なるため 最低風量・最低電力 直接入力ロジック反映から除外する
    if H_A['type'] == PROCESS_TYPE_3:
        print(PROCESS_TYPE_3)

        import jjjexperiment.latent_load.section4_2_a as jjj_latent_dc_a
        E_E_fan_H_d_t = jjj_latent_dc_a.get_E_E_fan_H_d_t(V_hs_vent_d_t, q_hs_H_d_t, H_A['f_SFP_H'])

    elif H_A['type'] in [PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_4]:
        print(H_A['type'])

        # [F25-01] 最低風量・最低電力 直接入力
        match injector.get(AppConfig).H.input_V_hs_min:
            case 最低風量直接入力.入力しない:
                print(最低風量直接入力.入力しない)

                # 従来式
                E_E_fan_H_d_t = \
                    dc_a.get_E_E_fan_H_d_t(
                        # ルームエアコンファン(P_rac_fan) OR 循環ファン(P_fan)
                        P_rac_fan_rtd_H if H_A['type'] == PROCESS_TYPE_2 else H_A['P_fan_rtd_H']
                        , V_hs_vent_d_t  # 上書きナシ
                        , V_hs_supply_d_t
                        , V_hs_dsgn_H
                        , q_hs_H_d_t  # W
                        , H_A['f_SFP_H'])  # NOTE: 従来式は標準値固定だがカスタム値を反映

            case 最低風量直接入力.入力する:
                print(最低風量直接入力.入力する)

                # V_hs_vent_d_t の上書き
                assert V_hs_vent_d_t.shape == Array8760.shape

                V_hs_min_H = injector.get(AppConfig).H.V_hs_min
                match injector.get(AppConfig).H.general_ventilation:
                    case True:
                        # 全般換気あり
                        # CHECK: 仕様の置換対象は V_vent_g_i かも
                        V_hs_vent_d_t: Array8760 = np.maximum(V_hs_min_H, V_hs_vent_d_t)
                    case False:
                        # 全般換気なし
                        H = np.array([hcm == HCM.暖房期 for hcm in HCM])
                        V_hs_vent_d_t[H] = V_hs_min_H
                    case _:
                        raise ValueError

                match injector.get(AppConfig).H.input_E_E_fan_min:
                    case 最低電力直接入力.入力しない.value:
                        print(最低電力直接入力.入力しない)

                        # 従来式
                        E_E_fan_H_d_t = \
                            dc_a.get_E_E_fan_H_d_t(
                                # ルームエアコンファン(P_rac_fan) OR 循環ファン(P_fan)
                                P_rac_fan_rtd_H if H_A['type'] == PROCESS_TYPE_2 else H_A['P_fan_rtd_H']
                                , V_hs_vent_d_t  # 上書きアリ
                                , V_hs_supply_d_t
                                , V_hs_dsgn_H
                                , q_hs_H_d_t  # W
                                , H_A['f_SFP_H'])  # NOTE: 従来式は標準値固定だがカスタム値を反映

                    case 最低電力直接入力.入力する.value:
                        print(最低電力直接入力.入力する)

                        E_E_fan_min_H = injector.get(AppConfig).H.E_E_fan_min
                        E_E_fan_logic = injector.get(AppConfig).H.E_E_fan_logic

                        import jjjexperiment.ac_min_volume_input.section4_2_a as jjj_V_min_input
                        E_E_fan_H_d_t = \
                            jjj_V_min_input.get_E_E_fan(
                                E_E_fan_logic
                                # ルームエアコンファン(P_rac_fan) OR 循環ファン(P_fan)
                                , P_rac_fan_rtd_H if H_A['type'] == PROCESS_TYPE_2 else H_A['P_fan_rtd_H']
                                , V_hs_vent_d_t  # 上書きアリ
                                , V_hs_supply_d_t
                                , V_hs_dsgn_H
                                , q_hs_H_d_t  # W
                                , E_E_fan_min_H)
                    case _:
                        raise ValueError
            case _:
                raise ValueError
    else:
        raise ValueError

    E_E_H_d_t: np.ndarray
    """日付dの時刻tにおける1時間当たり 暖房時の消費電力量 [kWh/h]"""

    if H_A['type'] == PROCESS_TYPE_1 or H_A['type'] == PROCESS_TYPE_3:
        E_E_H_d_t \
            = jjj_dc_a.calc_E_E_H_d_t_type1_and_type3(
                type = H_A['type'],
                E_E_fan_H_d_t = E_E_fan_H_d_t,
                q_hs_H_d_t = q_hs_H_d_t,
                Theta_hs_out_d_t = Theta_hs_out_d_t,
                Theta_hs_in_d_t = Theta_hs_in_d_t,
                Theta_ex_d_t = Theta_ex_d_t,  # 空気温度
                V_hs_supply_d_t = V_hs_supply_d_t,  # 風量
                q_hs_rtd_C = C_A['q_hs_rtd_C'],  # 定格冷房能力※
                q_hs_min_H = H_A['q_hs_min_H'],  # 最小暖房能力
                # 中間
                q_hs_mid_H = H_A['q_hs_mid_H'],
                P_hs_mid_H = H_A['P_hs_mid_H'],
                V_fan_mid_H = H_A['V_fan_mid_H'],
                P_fan_mid_H = H_A['P_fan_mid_H'],
                # 定格
                q_hs_rtd_H = H_A['q_hs_rtd_H'],
                P_fan_rtd_H = H_A['P_fan_rtd_H'],
                V_fan_rtd_H = H_A['V_fan_rtd_H'],
                P_hs_rtd_H = H_A['P_hs_rtd_H'],
                EquipmentSpec = H_A['EquipmentSpec']
            )
    elif H_A['type'] == PROCESS_TYPE_2:
        E_E_H_d_t \
            = jjj_dc_a.calc_E_E_H_d_t_type2(
                type = H_A['type'],
                region = region,
                climateFile = climateFile,
                E_E_fan_H_d_t = E_E_fan_H_d_t,
                q_hs_H_d_t = q_hs_H_d_t,
                e_rtd_H = e_rtd_H,
                q_rtd_H = q_rtd_H,
                q_rtd_C = q_rtd_C,
                q_max_H = q_max_H,
                q_max_C = q_max_C,
                input_C_af_H = input_C_af_H,
                dualcompressor_H = dualcompressor_H
            )
    elif H_A['type'] == PROCESS_TYPE_4:
        E_E_H_d_t \
            = jjj_dc_a.calc_E_E_H_d_t_type4(
                case_name = case_name,
                type = H_A['type'],
                region = region,
                climateFile = climateFile,
                E_E_fan_H_d_t = E_E_fan_H_d_t,
                q_hs_H_d_t = q_hs_H_d_t,
                V_hs_supply_d_t = V_hs_supply_d_t,
                P_rac_fan_rtd_H = P_rac_fan_rtd_H,
                simu_R_H = simu_R_H,
                spec = spec,
                Theta_real_inner = T_real,
                RH_real_inner = RH_real
            )
    else:
        raise Exception("暖房方式が不正です。")

    alpha_UT_H_A: float = get_alpha_UT_H_A(region)
    """未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数"""
    Q_UT_H_A_d_t: np.ndarray = np.sum(Q_UT_H_d_t_i, axis=0)
    """未処理暖房負荷の全機器合計(MJ/h)"""
    E_UT_H_d_t: np.ndarray = Q_UT_H_A_d_t * alpha_UT_H_A
    """未処理暖房負荷の設計一次エネルギー消費量相当値(MJ/h)"""
    _logger.NDdebug("E_UT_H_d_t", E_UT_H_d_t)

    df_output2 = pd.DataFrame(index = pd.date_range(datetime(2023,1,1,1,0,0), datetime(2024,1,1,0,0,0), freq='h'))
    df_output2['Q_UT_H_d_A_t [MJ/h]']        = Q_UT_H_A_d_t
    df_output2['Theta_hs_H_out_d_t [℃]']    = Theta_hs_out_d_t
    df_output2['Theta_hs_H_in_d_t [℃]']     = Theta_hs_in_d_t
    df_output2['Theta_ex_d_t [℃]']          = Theta_ex_d_t
    df_output2['V_hs_supply_H_d_t [m3/h]']  = V_hs_supply_d_t
    df_output2['V_hs_vent_H_d_t [m3/h]']    = V_hs_vent_d_t
    df_output2['C_df_H_d_t [-]']            = C_df_H_d_t

    ##### 冷房消費電力の計算（kWh/h）

    def get_V_hs_dsgn_C(C_A: dict, q_rtd_C: float):
        if C_A['type'] == PROCESS_TYPE_1 or C_A['type'] == PROCESS_TYPE_3:
            V_fan_rtd_C = C_A['V_fan_rtd_C']
        elif C_A['type'] == PROCESS_TYPE_2 or C_A['type'] == PROCESS_TYPE_4:
            V_fan_rtd_C = dc_spec.get_V_fan_rtd_C(q_rtd_C)
        else:
            raise Exception("冷房方式が不正です。")

        return dc_spec.get_V_fan_dsgn_C(V_fan_rtd_C)

    V_hs_dsgn_C = C_A['V_hs_dsgn_C'] if 'V_hs_dsgn_C' in C_A else get_V_hs_dsgn_C(C_A, q_rtd_C)
    """ 冷房時の送風機の設計風量[m3/h] """
    V_hs_dsgn_H: float = None  # NOTE: 冷房負荷計算時は空
    """ 暖房時の送風機の設計風量[m3/h] """

    if C_A['type'] == PROCESS_TYPE_4:
        spec, cdtn, T_real, RH_real = jjjexperiment.input.get_rac_catalog_spec(input_data, TH_FC=False)
        R2, R1, R0, P_rac_fan_rtd_C = jjjexperiment.denchu_1.calc_R_and_Pc_C(spec, cdtn)
        P_rac_fan_rtd_C = 1000 * P_rac_fan_rtd_C  # kW -> W
        simu_R_C = jjjexperiment.denchu_2.simu_R(R2, R1, R0)

        """ 電柱研モデルのモデリング定数の確認のためのCSV出力 """
        df_denchu_consts = jjjexperiment.denchu_1 \
            .get_DataFrame_denchu_modeling_consts(spec, cdtn, R2, R1, R0, T_real, RH_real, P_rac_fan_rtd_C)
        df_denchu_consts.to_csv(case_name + jjj_consts.version_info() + '_denchu_consts_C_output.csv', encoding='cp932')

        del cdtn, R2, R1, R0  # NOTE: 以降不要
    else:
        P_rac_fan_rtd_C: float = V_hs_dsgn_C * C_A['f_SFP_C']
    """定格冷房能力運転時の送風機の消費電力(W)"""
    _logger.info(f"P_rac_fan_rtd_C [W]: {P_rac_fan_rtd_C}")

    E_C_UT_d_t: np.ndarray
    """冷房設備の未処理冷房負荷の設計一次エネルギー消費量相当値(MJ/h)"""

    E_C_UT_d_t, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, V_hs_vent_d_t, _\
        = jjj_dc.calc_Q_UT_A(case_name, A_A, A_MR, A_OR, r_env, mu_H, mu_C,
            None, C_A['q_hs_rtd_C'],
            q_rtd_H, q_rtd_C, q_max_H, q_max_C, V_hs_dsgn_H, V_hs_dsgn_C, Q, C_A['VAV'], C_A['general_ventilation'], hs_CAV,
            C_A['duct_insulation'], region, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i,
            C_A['type'], input_C_af_H, input_C_af_C,
            r_A_ufvnt, underfloor_insulation, underfloor_air_conditioning_air_supply, YUCACO_r_A_ufvnt, climateFile)
    _logger.NDdebug("V_hs_supply_d_t", V_hs_supply_d_t)
    _logger.NDdebug("V_hs_vent_d_t", V_hs_vent_d_t)

    # (4) 日付dの時刻tにおける1時間当たりの熱源機の平均冷房能力(-)
    q_hs_CS_d_t, q_hs_CL_d_t = dc_a.get_q_hs_C_d_t_2(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, region)

    if (C_A['type'] == PROCESS_TYPE_1 or C_A['type'] == PROCESS_TYPE_3):
        # (4) 潜熱/顕熱を使用せずに全熱負荷を再計算する
        q_hs_C_d_t = dc_a.get_q_hs_C_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, region)
    else:
        # 潜熱/顕熱を使用する
        q_hs_C_d_t = q_hs_CS_d_t + q_hs_CL_d_t

    if C_A['type'] == PROCESS_TYPE_3:
        print(PROCESS_TYPE_3)

        import jjjexperiment.latent_load.section4_2_a as jjj_latent_dc_a
        E_E_fan_C_d_t = jjj_latent_dc_a.get_E_E_fan_C_d_t(V_hs_vent_d_t, q_hs_C_d_t, C_A['f_SFP_C'])

    elif C_A['type'] in [PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_4]:
        print(C_A['type'])

        # [F25-01] 最低風量・最低電力 直接入力
        match injector.get(AppConfig).C.input_V_hs_min:
            case 最低風量直接入力.入力しない:
                print(最低風量直接入力.入力しない)

                # 従来式
                E_E_fan_C_d_t = \
                    dc_a.get_E_E_fan_C_d_t(
                        # ルームエアコンファン(P_rac_fan) OR 循環ファン(P_fan)
                        P_rac_fan_rtd_C if C_A['type'] == PROCESS_TYPE_2 else C_A['P_fan_rtd_C']
                        , V_hs_vent_d_t  # 上書きナシ
                        , V_hs_supply_d_t
                        , V_hs_dsgn_C
                        , q_hs_C_d_t  # W
                        , C_A['f_SFP_C'])  # NOTE: 従来式は標準値固定だがカスタム値を反映

            case 最低風量直接入力.入力する:
                print(最低風量直接入力.入力する)

                # V_hs_vent_d_t の上書き
                assert V_hs_vent_d_t.shape == Array8760.shape

                V_hs_min_C = injector.get(AppConfig).C.V_hs_min
                match injector.get(AppConfig).C.general_ventilation:
                    case True:
                        # 全般換気あり
                        # CHECK: 仕様の置換対象は V_vent_g_i かも
                        V_hs_vent_d_t: Array8760 = np.maximum(V_hs_min_C, V_hs_vent_d_t)
                    case False:
                        # 全般換気なし
                        C = np.array([hcm == HCM.冷房期 for hcm in HCM])
                        V_hs_vent_d_t[C] = V_hs_min_C
                    case _:
                        raise ValueError

                match injector.get(AppConfig).C.input_E_E_fan_min:
                    case 最低電力直接入力.入力しない.value:
                        print(最低電力直接入力.入力しない)

                        # 従来式
                        E_E_fan_C_d_t = \
                            dc_a.get_E_E_fan_C_d_t(
                                # ルームエアコンファン(P_rac_fan) OR 循環ファン(P_fan)
                                P_rac_fan_rtd_C if C_A['type'] == PROCESS_TYPE_2 else C_A['P_fan_rtd_C']
                                , V_hs_vent_d_t  # 上書きアリ
                                , V_hs_supply_d_t
                                , V_hs_dsgn_C
                                , q_hs_C_d_t  # W
                                , C_A['f_SFP_C'])  # NOTE: 従来式は標準値固定だがカスタム値を反映

                    case 最低電力直接入力.入力する.value:
                        print(最低電力直接入力.入力する)

                        E_E_fan_min_C = injector.get(AppConfig).C.E_E_fan_min
                        E_E_fan_logic = injector.get(AppConfig).C.E_E_fan_logic

                        import jjjexperiment.ac_min_volume_input.section4_2_a as jjj_V_min_input
                        E_E_fan_C_d_t = \
                            jjj_V_min_input.get_E_E_fan_d_t(
                                E_E_fan_logic
                                # ルームエアコンファン(P_rac_fan) OR 循環ファン(P_fan)
                                , P_rac_fan_rtd_C if C_A['type'] == PROCESS_TYPE_2 else C_A['P_fan_rtd_C']
                                , V_hs_vent_d_t  # 上書きアリ
                                , V_hs_supply_d_t
                                , V_hs_dsgn_C
                                , q_hs_C_d_t  # W
                                , E_E_fan_min_C)
                    case _:
                        raise ValueError
            case _:
                raise ValueError
    else:
        raise ValueError

    E_E_C_d_t: np.ndarray
    """日付dの時刻tにおける1時間当たりの冷房時の消費電力量(kWh/h)"""

    if C_A['type'] == PROCESS_TYPE_1 or C_A['type'] == PROCESS_TYPE_3:
        E_E_C_d_t = jjj_dc_a.calc_E_E_C_d_t_type1_and_type3(
            type = C_A['type'],
            region = region,
            E_E_fan_C_d_t = E_E_fan_C_d_t,
            Theta_hs_out_d_t = Theta_hs_out_d_t,
            Theta_hs_in_d_t = Theta_hs_in_d_t,
            Theta_ex_d_t = Theta_ex_d_t,
            V_hs_supply_d_t = V_hs_supply_d_t,
            X_hs_out_d_t = X_hs_out_d_t,
            X_hs_in_d_t = X_hs_in_d_t,
            q_hs_min_C = C_A['q_hs_min_C'],
            # 中間
            q_hs_mid_C = C_A['q_hs_mid_C'],
            P_hs_mid_C = C_A['P_hs_mid_C'],
            V_fan_mid_C = C_A['V_fan_mid_C'],
            P_fan_mid_C = C_A['P_fan_mid_C'],
            # 定格
            q_hs_rtd_C = C_A['q_hs_rtd_C'],
            P_fan_rtd_C = C_A['P_fan_rtd_C'],
            V_fan_rtd_C = C_A['V_fan_rtd_C'],
            P_hs_rtd_C = C_A['P_hs_rtd_C'],
            EquipmentSpec = C_A['EquipmentSpec']
        )
    elif C_A['type'] == PROCESS_TYPE_2:
        E_E_C_d_t = jjj_dc_a.calc_E_E_C_d_t_type2(
            type = C_A['type'],
            region = region,
            climateFile = climateFile,
            E_E_fan_C_d_t = E_E_fan_C_d_t,
            q_hs_CS_d_t = q_hs_CS_d_t,
            q_hs_CL_d_t = q_hs_CL_d_t,
            e_rtd_C = e_rtd_C,
            q_rtd_C = q_rtd_C,
            q_max_C = q_max_C,
            input_C_af_C = input_C_af_C,
            dualcompressor_C = dualcompressor_C
        )
    elif C_A['type'] == PROCESS_TYPE_4:
        E_E_C_d_t = jjj_dc_a.calc_E_E_C_d_t_type4(
            case_name = case_name,
            type = C_A['type'],
            region = region,
            climateFile = climateFile,
            E_E_fan_C_d_t = E_E_fan_C_d_t,
            q_hs_C_d_t = q_hs_CS_d_t + q_hs_CL_d_t,
            V_hs_supply_d_t = V_hs_supply_d_t,
            P_rac_fan_rtd_C = P_rac_fan_rtd_C,
            simu_R_C = simu_R_C,
            spec = spec,
            Theta_real_inner = T_real,
            RH_real_inner = RH_real
        )
    else:
        raise Exception("冷房方式が不正です。")

    ##### 計算結果のまとめ

    f_prim: float       = get_f_prim()                              # 電気の量 1kWh を熱量に換算する係数(kJ/kWh)
    # CHECK: E_C_UT_d_t, E_H_UT_d_t 変数名表現の統一
    E_H_d_t: np.ndarray = E_E_H_d_t * f_prim / 1000 + E_UT_H_d_t    #1 時間当たりの暖房設備の設計一次エネルギー消費量(MJ/h)
    E_C_d_t: np.ndarray = E_E_C_d_t * f_prim / 1000 + E_C_UT_d_t    #1 時間当たりの冷房設備の設計一次エネルギー消費量(MJ/h)
    E_H                 = np.sum(E_H_d_t)                           #1 年当たりの暖房設備の設計一次エネルギー消費量(MJ/年)
    E_C                 = np.sum(E_C_d_t)                           #1 年当たりの冷房設備の設計一次エネルギー消費量(MJ/年)

    _logger.info(f"E_H [MJ/year]: {E_H}")
    _logger.info(f"E_C [MJ/year]: {E_C}")

    print('E_H [MJ/year]: ', E_H, ', E_C [MJ/year]: ', E_C)

    df_output1 = pd.DataFrame(index = ['合計値'])
    df_output1['E_H [MJ/year]'] = E_H
    df_output1['E_C [MJ/year]'] = E_C
    df_output1.to_csv(case_name + jjj_consts.version_info() + '_output1.csv', encoding = 'cp932')

    df_output2['Theta_hs_C_out_d_t [℃]']    = Theta_hs_out_d_t
    df_output2['Theta_hs_C_in_d_t [℃]']     = Theta_hs_in_d_t
    df_output2['Theta_ex_d_t [℃]']          = Theta_ex_d_t
    df_output2['V_hs_supply_C_d_t [m3/h]']  = V_hs_supply_d_t
    df_output2['V_hs_vent_C_d_t [m3/h]']    = V_hs_vent_d_t
    df_output2['E_H_d_t [MJ/h]']            = E_H_d_t
    df_output2['E_C_d_t [MJ/h]']            = E_C_d_t
    df_output2['E_E_H_d_t [kWh/h]']         = E_E_H_d_t
    df_output2['E_E_C_d_t [kWh/h]']         = E_E_C_d_t
    df_output2['E_UT_H_d_t [MJ/h]']         = E_UT_H_d_t
    df_output2['E_UT_C_d_t [MJ/h]']         = E_C_UT_d_t
    df_output2['L_H_d_t [MJ/h]']            = L_H_d_t
    df_output2['L_CS_d_t [MJ/h]']           = L_CS_d_t
    df_output2['L_CL_d_t [MJ/h]']           = L_CL_d_t
    df_output2['E_E_fan_H_d_t [kWh/h]']     = E_E_fan_H_d_t
    df_output2['E_E_fan_C_d_t [kWh/h]']     = E_E_fan_C_d_t
    df_output2['q_hs_H_d_t [Wh/h]']         = q_hs_H_d_t
    df_output2['q_hs_CS_d_t [Wh/h]']        = q_hs_CS_d_t
    df_output2['q_hs_CL_d_t [Wh/h]']        = q_hs_CL_d_t
    df_output2.to_csv(case_name + jjj_consts.version_info() + '_output2.csv', encoding = 'cp932')

    # NOTE: 結合テストで確認したい値を返すのに使用します
    if test_mode:
        i = TestInputPickups(q_rtd_C, q_rtd_H, q_max_C, q_max_H, e_rtd_C, e_rtd_H)
        r = ResultSummary(E_C, E_H)
        # NOTE: 今後の拡張を想定して既存コードが壊れにくい辞書型にしています
        return {'TInput':i, 'TValue':r}
