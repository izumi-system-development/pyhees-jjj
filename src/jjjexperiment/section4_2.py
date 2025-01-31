import numpy as np
import pandas as pd
from datetime import datetime

from pyhees.section11_1 import calc_h_ex, load_climate, get_Theta_ex, get_X_ex, get_climate_df
from pyhees.section11_2 import calc_I_s_d_t

# エアーコンディショナー
import pyhees.section4_3 as rac

# 床下
import pyhees.section3_1 as ld
import pyhees.section3_1_e as uf

# ダクト式セントラル空調機
import pyhees.section4_2 as dc
import pyhees.section4_2_a as dc_a

""" JJJ_EXPERIMENT OVERRIDE """

""" JJJ_EXPERIMENT ORIGINAL """

import jjjexperiment.constants as constants
from jjjexperiment.constants import PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_3, PROCESS_TYPE_4
from jjjexperiment.logger import LimitedLoggerAdapter as _logger  # デバッグ用ロガー
from jjjexperiment.options import *
from jjjexperiment.helper import *

import jjjexperiment.carryover_heat as jjj_carryover_heat

# DIコンテナー
from injector import Injector
from jjjexperiment.di_container import *

# NOTE: section4_2 の同名の関数の改変版
@constants.jjjexperiment_clone
def calc_Q_UT_A(case_name, A_A, A_MR, A_OR, r_env, mu_H, mu_C, q_hs_rtd_H, q_hs_rtd_C, q_rtd_H, q_rtd_C, q_max_H, q_max_C, V_hs_dsgn_H, V_hs_dsgn_C, Q,
            VAV, general_ventilation, hs_CAV, duct_insulation, region, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i,
            type, input_C_af_H, input_C_af_C,
            r_A_ufvnt, underfloor_insulation, underfloor_air_conditioning_air_supply, YUCACO_r_A_ufvnt, climateFile):
    """未処理負荷と機器の計算に必要な変数を取得"""

    # NOTE: 暖房・冷房で二回実行される。q_hs_rtd_h, q_hs_rtd_C のどちらが None かで判別可能

    dimodule = JJJExperimentModule()
    dimodule.set_houseinfo(SampleHouseInfo(A_A, A_MR, A_OR, r_A_ufvnt, None))
    di = Injector(dimodule)  # こちらのインスタンスのみを使用する

    di.get(SampleHouseInfo)
    ha_ca_holder = di.get(HaCaInputHolder)
    ha_ca_holder.q_hs_rtd_H = q_hs_rtd_H
    ha_ca_holder.q_hs_rtd_C = q_hs_rtd_C

    R_g = constants.R_g  # 追加0416

    df_output  = pd.DataFrame(index = pd.date_range(datetime(2023,1,1,1,0,0), datetime(2024,1,1,0,0,0), freq='h'))
    df_output2 = pd.DataFrame()
    df_output3 = pd.DataFrame()

    # 熱繰越調査用出力ファイル
    df_carryover_output  = pd.DataFrame(index = pd.date_range(datetime(2023,1,1,1,0,0), datetime(2024,1,1,0,0,0), freq='h'))

    # 気象条件
    if climateFile == '-':
        climate = load_climate(region)
    else:
        climate = pd.read_csv(climateFile, nrows=24 * 365, encoding="SHIFT-JIS")
    Theta_ex_d_t = get_Theta_ex(climate)
    X_ex_d_t = get_X_ex(climate)

    J_d_t = calc_I_s_d_t(0, 0, get_climate_df(climate))
    h_ex_d_t = calc_h_ex(X_ex_d_t, Theta_ex_d_t)

    df_output['Theta_ex_d_t']  = Theta_ex_d_t
    df_output['X_ex_d_t']      = X_ex_d_t

    h_ex_d_t = calc_h_ex(X_ex_d_t, Theta_ex_d_t)

    df_output['J_d_t']    = J_d_t.to_numpy()
    df_output['h_ex_d_t'] = h_ex_d_t

    #主たる居室・その他居室・非居室の面積
    A_HCZ_i = np.array([ld.get_A_HCZ_i(i, A_A, A_MR, A_OR) for i in range(1, 6)])
    A_HCZ_R_i = np.array([ld.get_A_HCZ_R_i(i) for i in range(1, 6)])
    A_NR = ld.get_A_NR(A_A, A_MR, A_OR)

    df_output2['A_HCZ_i'] = A_HCZ_i
    df_output2['A_HCZ_R_i'] = A_HCZ_R_i
    df_output3['A_NR'] = [A_NR]

    # (67)  水の蒸発潜熱
    L_wtr = dc.get_L_wtr()
    df_output3['L_wtr'] = [L_wtr]

    # (66d)　非居室の在室人数
    n_p_NR_d_t = dc.calc_n_p_NR_d_t(A_NR)
    df_output['n_p_NR_d_t'] = n_p_NR_d_t

    # (66c)　その他居室の在室人数
    n_p_OR_d_t = dc.calc_n_p_OR_d_t(A_OR)
    df_output['n_p_OR_d_t'] = n_p_OR_d_t

    # (66b)　主たる居室の在室人数
    n_p_MR_d_t = dc.calc_n_p_MR_d_t(A_MR)
    df_output['n_p_MR_d_t'] = n_p_MR_d_t

    # (66a)　在室人数
    n_p_d_t = dc.get_n_p_d_t(n_p_MR_d_t, n_p_OR_d_t, n_p_NR_d_t)
    df_output['n_p_d_t'] = n_p_d_t

    # 人体発熱
    q_p_H = dc.get_q_p_H()
    q_p_CS = dc.get_q_p_CS()
    q_p_CL = dc.get_q_p_CL()
    df_output3['q_p_H'] = [q_p_H]
    df_output3['q_p_CS'] = [q_p_CS]
    df_output3['q_p_CL'] = [q_p_CL]

    # (65d)　非居室の内部発湿
    w_gen_NR_d_t = dc.calc_w_gen_NR_d_t(A_NR)
    df_output['w_gen_NR_d_t'] = w_gen_NR_d_t

    # (65c)　その他居室の内部発湿
    w_gen_OR_d_t = dc.calc_w_gen_OR_d_t(A_OR)
    df_output['w_gen_OR_d_t'] = w_gen_OR_d_t

    # (65b)　主たる居室の内部発湿
    w_gen_MR_d_t = dc.calc_w_gen_MR_d_t(A_MR)
    df_output['w_gen_MR_d_t'] = w_gen_MR_d_t

    # (65a)　内部発湿
    w_gen_d_t = dc.get_w_gen_d_t(w_gen_MR_d_t, w_gen_OR_d_t, w_gen_NR_d_t)
    df_output['w_gen_d_t'] = w_gen_d_t

    # (64d)　非居室の内部発熱
    q_gen_NR_d_t = dc.calc_q_gen_NR_d_t(A_NR)
    df_output['q_gen_NR_d_t'] = q_gen_NR_d_t

    # (64c)　その他居室の内部発熱
    q_gen_OR_d_t = dc.calc_q_gen_OR_d_t(A_OR)
    df_output['q_gen_OR_d_t'] = q_gen_OR_d_t

    # (64b)　主たる居室の内部発熱
    q_gen_MR_d_t = dc.calc_q_gen_MR_d_t(A_MR)
    df_output['q_gen_MR_d_t'] = q_gen_MR_d_t

    # (64a)　内部発熱
    q_gen_d_t = dc.get_q_gen_d_t(q_gen_MR_d_t, q_gen_OR_d_t, q_gen_NR_d_t)
    df_output['q_gen_d_t'] = q_gen_d_t

    # (63)　局所排気量
    V_vent_l_NR_d_t = dc.get_V_vent_l_NR_d_t()
    V_vent_l_OR_d_t = dc.get_V_vent_l_OR_d_t()
    V_vent_l_MR_d_t = dc.get_V_vent_l_MR_d_t()
    V_vent_l_d_t = dc.get_V_vent_l_d_t(V_vent_l_MR_d_t, V_vent_l_OR_d_t, V_vent_l_NR_d_t)
    df_output = df_output.assign(
        V_vent_l_NR_d_t = V_vent_l_NR_d_t,
        V_vent_l_OR_d_t = V_vent_l_OR_d_t,
        V_vent_l_MR_d_t = V_vent_l_MR_d_t,
        V_vent_l_d_t = V_vent_l_d_t
    )

    # (62)　全般換気量
    V_vent_g_i = dc.get_V_vent_g_i(A_HCZ_i, A_HCZ_R_i)
    df_output2['V_vent_g_i'] = V_vent_g_i

    # (61)　間仕切の熱貫流率
    U_prt = dc.get_U_prt()
    df_output3['U_prt'] = [U_prt]

    # (60)　非居室の間仕切の面積
    A_prt_i = dc.get_A_prt_i(A_HCZ_i, r_env, A_MR, A_NR, A_OR)
    df_output3['r_env'] = [r_env]
    df_output2['A_prt_i'] = A_prt_i

    # (59)　等価外気温度
    Theta_SAT_d_t = dc.get_Theta_SAT_d_t(Theta_ex_d_t, J_d_t)
    df_output['Theta_SAT_d_t'] = Theta_SAT_d_t

    # (58)　断熱区画外を通るダクトの長さ
    l_duct_ex_i = dc.get_l_duct_ex_i(A_A)
    df_output2['l_duct_ex_i'] = l_duct_ex_i

    # (57)　断熱区画内を通るダクト長さ
    l_duct_in_i = dc.get_l_duct_in_i(A_A)
    df_output2['l_duct_in_i'] = l_duct_in_i

    # (56)　ダクト長さ
    l_duct_i = dc.get_l_duct__i(l_duct_in_i, l_duct_ex_i)
    df_output2['l_duct_i'] = l_duct_i

    # (51)　負荷バランス時の居室の絶対湿度
    X_star_HBR_d_t = dc.get_X_star_HBR_d_t(X_ex_d_t, region)  # X_ex_d_t [g/kg(DA)] 想定
    df_output['X_star_HBR_d_t'] = X_star_HBR_d_t

    # (50)　負荷バランス時の居室の室温
    Theta_star_HBR_d_t = dc.get_Theta_star_HBR_d_t(Theta_ex_d_t, region)
    df_output['Theta_star_HBR_d_t'] = Theta_star_HBR_d_t

    # (55)　小屋裏の空気温度
    Theta_attic_d_t = dc.get_Theta_attic_d_t(Theta_SAT_d_t, Theta_star_HBR_d_t)
    df_output['Theta_attic_d_t'] = Theta_attic_d_t

    # (54)　ダクトの周囲の空気温度
    Theta_sur_d_t_i = dc.get_Theta_sur_d_t_i(Theta_star_HBR_d_t, Theta_attic_d_t, l_duct_in_i, l_duct_ex_i, duct_insulation)
    df_output = df_output.assign(
        Theta_sur_d_t_i_1 = Theta_sur_d_t_i[0],
        Theta_sur_d_t_i_2 = Theta_sur_d_t_i[1],
        Theta_sur_d_t_i_3 = Theta_sur_d_t_i[2],
        Theta_sur_d_t_i_4 = Theta_sur_d_t_i[3],
        Theta_sur_d_t_i_5 = Theta_sur_d_t_i[4]
    )

    # (40)　熱源機の風量を計算するための熱源機の出力
    # NOTE: 潜熱バグフィックスが有効でないと誤った数字となります
    Q_hat_hs_d_t, Q_hat_hs_CS_d_t = dc.calc_Q_hat_hs_d_t(Q, A_A, V_vent_l_d_t, V_vent_g_i, mu_H, mu_C, J_d_t, q_gen_d_t, n_p_d_t, q_p_H,
                                     q_p_CS, q_p_CL, X_ex_d_t, w_gen_d_t, Theta_ex_d_t, L_wtr, region)
    df_output['Q_hat_hs_d_t'] = Q_hat_hs_d_t

    # (39)　熱源機の最低風量
    V_hs_min = dc.get_V_hs_min(V_vent_g_i)
    df_output3['V_hs_min'] = [V_hs_min]

    ####################################################################################################################
    if type == PROCESS_TYPE_1 or type == PROCESS_TYPE_3:
        # (38)
        Q_hs_rtd_C = dc.get_Q_hs_rtd_C(q_hs_rtd_C)

        # (37)
        Q_hs_rtd_H = dc.get_Q_hs_rtd_H(q_hs_rtd_H)
    elif type == PROCESS_TYPE_2 or type == PROCESS_TYPE_4:
        # (38)　冷房時の熱源機の定格出力
        Q_hs_rtd_C = dc.get_Q_hs_rtd_C(q_rtd_C)  #ルームエアコンディショナの定格能力 q_rtd_C を入力するよう書き換え

        # (37)　暖房時の熱源機の定格出力
        Q_hs_rtd_H = dc.get_Q_hs_rtd_H(q_rtd_H)  #ルームエアコンディショナの定格能力 q_rtd_H を入力するよう書き換え
    else:
        raise Exception('設備機器の種類の入力が不正です。')

    df_output3['Q_hs_rtd_C'] = [Q_hs_rtd_C]
    df_output3['Q_hs_rtd_H'] = [Q_hs_rtd_H]
    ####################################################################################################################

    # (36)　VAV 調整前の熱源機の風量
    if hs_CAV:
        H, C, M = dc_a.get_season_array_d_t(region)
        V_dash_hs_supply_d_t = np.zeros(24 * 365)
        V_dash_hs_supply_d_t[H] = V_hs_dsgn_H or 0
        V_dash_hs_supply_d_t[C] = V_hs_dsgn_C or 0
        V_dash_hs_supply_d_t[M] = 0
    else:
        if Q_hs_rtd_H is not None:
            updated_V_hs_dsgn_H = V_hs_dsgn_H or 0
        else:
            updated_V_hs_dsgn_H = None
        if Q_hs_rtd_C is not None:
            updated_V_hs_dsgn_C = V_hs_dsgn_C or 0
        else:
            updated_V_hs_dsgn_C = None

        if type == PROCESS_TYPE_3:
            # FIXME: 方式3が他方式と比較して大きくなる問題
            if updated_V_hs_dsgn_C is not None:
                # 冷房時 => 顕熱負荷のみ
                V_dash_hs_supply_d_t = dc.get_V_dash_hs_supply_d_t_2023(Q_hat_hs_CS_d_t, region, True)
            else:
                # 暖房 => 全熱負荷
                V_dash_hs_supply_d_t = dc.get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, region, True)
            df_output['V_dash_hs_supply_d_t'] = V_dash_hs_supply_d_t
        else:
            V_dash_hs_supply_d_t = dc.get_V_dash_hs_supply_d_t(V_hs_min, updated_V_hs_dsgn_H, updated_V_hs_dsgn_C, Q_hs_rtd_H, Q_hs_rtd_C, Q_hat_hs_d_t, region)
            df_output['V_dash_hs_supply_d_t'] = V_dash_hs_supply_d_t

    if VAV and constants.change_supply_volume_before_vav_adjust == VAVありなしの吹出風量.数式を統一する.value:
        # (45)　風量バランス
        r_supply_des_d_t_i = dc.get_r_supply_des_d_t_i_2023(region, L_CS_d_t_i, L_H_d_t_i)
        # (44)　VAV 調整前の吹き出し風量
        V_dash_supply_d_t_i = dc.get_V_dash_supply_d_t_i_2023(r_supply_des_d_t_i, V_dash_hs_supply_d_t, V_vent_g_i)

        df_output2['r_supply_des_i'] = None
        df_output = df_output.assign(
            r_supply_des_d_t_1 = r_supply_des_d_t_i[0],
            r_supply_des_d_t_2 = r_supply_des_d_t_i[1],
            r_supply_des_d_t_3 = r_supply_des_d_t_i[2],
            r_supply_des_d_t_4 = r_supply_des_d_t_i[3],
            r_supply_des_d_t_5 = r_supply_des_d_t_i[4]
        )
    else:
        # (45)　風量バランス
        r_supply_des_i = dc.get_r_supply_des_i(A_HCZ_i)
        # (44)　VAV 調整前の吹き出し風量
        V_dash_supply_d_t_i = dc.get_V_dash_supply_d_t_i(r_supply_des_i, V_dash_hs_supply_d_t, V_vent_g_i)

        df_output2['r_supply_des_i'] = r_supply_des_i
        df_output = df_output.assign(
            r_supply_des_d_t_1 = None,
            r_supply_des_d_t_2 = None,
            r_supply_des_d_t_3 = None,
            r_supply_des_d_t_4 = None,
            r_supply_des_d_t_5 = None
        )
    df_output = df_output.assign(
        V_dash_supply_d_t_1 = V_dash_supply_d_t_i[0],
        V_dash_supply_d_t_2 = V_dash_supply_d_t_i[1],
        V_dash_supply_d_t_3 = V_dash_supply_d_t_i[2],
        V_dash_supply_d_t_4 = V_dash_supply_d_t_i[3],
        V_dash_supply_d_t_5 = V_dash_supply_d_t_i[4]
    )

    # (53)　負荷バランス時の非居室の絶対湿度
    X_star_NR_d_t = dc.get_X_star_NR_d_t(X_star_HBR_d_t, L_CL_d_t_i, L_wtr, V_vent_l_NR_d_t, V_dash_supply_d_t_i, region)
    df_output['X_star_NR_d_t'] = X_star_NR_d_t

    # (52)　負荷バランス時の非居室の室温
    Theta_star_NR_d_t = dc.get_Theta_star_NR_d_t(Theta_star_HBR_d_t, Q, A_NR, V_vent_l_NR_d_t, V_dash_supply_d_t_i, U_prt,
                                              A_prt_i, L_H_d_t_i, L_CS_d_t_i, region)
    df_output['Theta_star_NR_d_t'] = Theta_star_NR_d_t

    # (49)　実際の非居室の絶対湿度
    X_NR_d_t = dc.get_X_NR_d_t(X_star_NR_d_t)
    df_output['X_NR_d_t'] = X_NR_d_t

    # (47)　実際の居室の絶対湿度
    X_HBR_d_t_i = dc.get_X_HBR_d_t_i(X_star_HBR_d_t)
    df_output = df_output.assign(
        X_HBR_d_t_1 = X_HBR_d_t_i[0],
        X_HBR_d_t_2 = X_HBR_d_t_i[1],
        X_HBR_d_t_3 = X_HBR_d_t_i[2],
        X_HBR_d_t_4 = X_HBR_d_t_i[3],
        X_HBR_d_t_5 = X_HBR_d_t_i[4]
    )

    """ 熱損失・熱取得を含む負荷バランス時の熱負荷 - 熱損失・熱取得を含む負荷バランス時(1) """
    # (11)　熱損失を含む負荷バランス時の非居室への熱移動
    Q_star_trs_prt_d_t_i = dc.get_Q_star_trs_prt_d_t_i(U_prt, A_prt_i, Theta_star_HBR_d_t, Theta_star_NR_d_t)
    df_output = df_output.assign(
        Q_star_trs_prt_d_t_i_1 = Q_star_trs_prt_d_t_i[0],
        Q_star_trs_prt_d_t_i_2 = Q_star_trs_prt_d_t_i[1],
        Q_star_trs_prt_d_t_i_3 = Q_star_trs_prt_d_t_i[2],
        Q_star_trs_prt_d_t_i_4 = Q_star_trs_prt_d_t_i[3],
        Q_star_trs_prt_d_t_i_5 = Q_star_trs_prt_d_t_i[4]
    )

    # (10)　熱取得を含む負荷バランス時の冷房潜熱負荷
    L_star_CL_d_t_i = dc.get_L_star_CL_d_t_i(L_CS_d_t_i, L_CL_d_t_i, region)
    df_output = df_output.assign(
        L_star_CL_d_t_i_1 = L_star_CL_d_t_i[0],
        L_star_CL_d_t_i_2 = L_star_CL_d_t_i[1],
        L_star_CL_d_t_i_3 = L_star_CL_d_t_i[2],
        L_star_CL_d_t_i_4 = L_star_CL_d_t_i[3],
        L_star_CL_d_t_i_5 = L_star_CL_d_t_i[4]
    )

    # NOTE: 熱繰越を行うverと行わないverで 同じ処理を異なるループの粒度で二重実装が必要です
    # 実装量/計算量 の多い仕様の場合には 過剰熱繰越ナシ(一般的なパターン) のみ実装として、オプション併用を拒否する仕様も検討しましょう
    if constants.carry_over_heat == 過剰熱量繰越計算.行う.value:

        # NOTE: 過剰熱繰越と併用しないオプションはここで実行を拒否します
        if constants.change_underfloor_temperature == 床下空調ロジック.変更する.value:
            raise PermissionError("この操作は実行に時間がかかるため併用できません。[過剰熱繰越と床下空調ロジック変更]")
            # NOTE: 過剰熱繰越の8760ループと床下空調ロジック変更の8760ループが合わさると
            # 一時間を超える実行時間になることを確認したため回避しています(2024/02)

        # インデックス順に更新対象
        L_star_CS_d_t_i = np.zeros((5, 24 * 365))
        L_star_H_d_t_i = np.zeros((5, 24 * 365))

        # 実際の居室・非居室の室温
        # TODO: 空からappendで0を誤利用しないロジックに書き換えてみる
        Theta_HBR_d_t_i = np.zeros((5, 24 * 365))
        Theta_NR_d_t = np.zeros(24 * 365)
        # 空でよいのか? 先頭から利用されるのか?
        # (46)(48)で計算されるものだが、それらの式は後ろであるため、
        # ここでは空(ただし先頭から利用)でよいのかチェックする

        carryovers = np.zeros((5, 24 * 365))

        # (19)　負荷バランス時の熱源機の入口における空気温度
        Theta_star_hs_in_d_t = dc.get_Theta_star_hs_in_d_t(Theta_star_NR_d_t)

        for t in range(0, 24 * 365):
            # TODO: 先頭時の扱いを考慮
            isFirst = (t == 0)

            # 季節から計算の必要性を判断
            H, C, M = dc.get_season_array_d_t(region)

            if H[t] and C[t]:
                raise ValueError("想定外の季節")
            elif isFirst:
                carryover = np.zeros((5, 1))
            # 暖房期 前時刻にて 暖かさに余裕があるとき
            elif H[t] and np.any(Theta_HBR_d_t_i[:, t-1:t] > Theta_star_HBR_d_t[t-1]):
                carryover = jjj_carryover_heat \
                    .calc_carryover(H[t], C[t], A_HCZ_i,
                                    Theta_HBR_d_t_i[:, t-1:t],
                                    Theta_star_HBR_d_t[t-1])
            # 冷房期 前時刻にて 涼しさに余裕があるとき
            elif C[t] and np.any(Theta_HBR_d_t_i[:, t-1:t] < Theta_star_HBR_d_t[t-1]):
                carryover = jjj_carryover_heat \
                    .calc_carryover(H[t], C[t], A_HCZ_i,
                                    Theta_HBR_d_t_i[:, t-1:t],
                                    Theta_star_HBR_d_t[t-1])
            else:
                carryover = np.zeros((5, 1))
                # 前時刻の Theta_HBR_d_t_i を使用するため
                # 空調がなくてもすぐ次のループに行かず (46)(48)式の計算は行う

            carryovers[:, t] = carryover[:, 0]  # 確認用

            # (8)　熱損失を含む負荷バランス時の暖房負荷
            L_star_H_d_t_i[:, t:t+1]  \
                = jjj_carryover_heat.get_L_star_H_i_2024(
                    H[t],
                    L_H_d_t_i[:5, t:t+1],
                    Q_star_trs_prt_d_t_i[:5, t:t+1],
                    carryover)

            # (9)　熱取得を含む負荷バランス時の冷房顕熱負荷
            L_star_CS_d_t_i[:, t:t+1]  \
                = jjj_carryover_heat.get_L_star_CS_i_2024(
                    C[t],
                    L_CS_d_t_i[:5, t:t+1],
                    Q_star_trs_prt_d_t_i[:5, t:t+1],
                    carryover)

            ####################################################################################################################
            if type == PROCESS_TYPE_1 or type == PROCESS_TYPE_3:
                # (33)
                L_star_CL_d_t = dc.get_L_star_CL_d_t(L_star_CL_d_t_i)

                # (32)
                L_star_CS_d_t = dc.get_L_star_CS_d_t(L_star_CS_d_t_i)

                # (31)
                L_star_CL_max_d_t = dc.get_L_star_CL_max_d_t(L_star_CS_d_t)

                # (30)
                L_star_dash_CL_d_t = dc.get_L_star_dash_CL_d_t(L_star_CL_max_d_t, L_star_CL_d_t)

                # (29)
                L_star_dash_C_d_t = dc.get_L_star_dash_C_d_t(L_star_CS_d_t, L_star_dash_CL_d_t)

                # (28)
                SHF_dash_d_t = dc.get_SHF_dash_d_t(L_star_CS_d_t, L_star_dash_C_d_t)

                # (27)
                Q_hs_max_C_d_t = dc.get_Q_hs_max_C_d_t_2024(type, q_hs_rtd_C, input_C_af_C)

                # (26)
                Q_hs_max_CL_d_t = dc.get_Q_hs_max_CL_d_t(Q_hs_max_C_d_t, SHF_dash_d_t, L_star_dash_CL_d_t)

                # (25)
                Q_hs_max_CS_d_t = dc.get_Q_hs_max_CS_d_t(Q_hs_max_C_d_t, SHF_dash_d_t)

                # (24)
                C_df_H_d_t = dc.get_C_df_H_d_t(Theta_ex_d_t, h_ex_d_t)

                # (23)
                Q_hs_max_H_d_t = dc.get_Q_hs_max_H_d_t_2024(type, q_hs_rtd_H, C_df_H_d_t, input_C_af_H)

            elif type == PROCESS_TYPE_2 or type == PROCESS_TYPE_4:
                # (24)　デフロストに関する暖房出力補正係数
                C_df_H_d_t = dc.get_C_df_H_d_t(Theta_ex_d_t, h_ex_d_t)

                # 最大暖房能力比
                q_r_max_H = rac.get_q_r_max_H(q_max_H, q_rtd_H)

                # 最大暖房出力比
                Q_r_max_H_d_t = rac.calc_Q_r_max_H_d_t(q_rtd_C, q_r_max_H, Theta_ex_d_t)

                # 最大暖房出力
                Q_max_H_d_t = rac.calc_Q_max_H_d_t(Q_r_max_H_d_t, q_rtd_H, Theta_ex_d_t, h_ex_d_t, input_C_af_H)
                Q_hs_max_H_d_t = Q_max_H_d_t

                # 最大冷房能力比
                q_r_max_C = rac.get_q_r_max_C(q_max_C, q_rtd_C)

                # 最大冷房出力比
                Q_r_max_C_d_t = rac.calc_Q_r_max_C_d_t(q_r_max_C, q_rtd_C, Theta_ex_d_t)

                # 最大冷房出力
                Q_max_C_d_t = rac.calc_Q_max_C_d_t(Q_r_max_C_d_t, q_rtd_C, input_C_af_C)
                Q_hs_max_C_d_t = Q_max_C_d_t

                # 冷房負荷最小顕熱比
                SHF_L_min_c = rac.get_SHF_L_min_c()

                # 最大冷房潜熱負荷
                L_max_CL_d_t = rac.get_L_max_CL_d_t(np.sum(L_CS_d_t_i, axis=0), SHF_L_min_c)

                # 補正冷房潜熱負荷
                L_dash_CL_d_t = rac.get_L_dash_CL_d_t(L_max_CL_d_t, np.sum(L_CL_d_t_i, axis=0))
                L_dash_C_d_t = rac.get_L_dash_C_d_t(np.sum(L_CS_d_t_i, axis=0), L_dash_CL_d_t)

                # 冷房負荷補正顕熱比
                SHF_dash_d_t = rac.get_SHF_dash_d_t(np.sum(L_CS_d_t_i, axis=0), L_dash_C_d_t)

                # 最大冷房顕熱出力, 最大冷房潜熱出力
                Q_max_CS_d_t = rac.get_Q_max_CS_d_t(Q_max_C_d_t, SHF_dash_d_t)
                Q_max_CL_d_t = rac.get_Q_max_CL_d_t(Q_max_C_d_t, SHF_dash_d_t, L_dash_CL_d_t)
                Q_hs_max_C_d_t = Q_max_C_d_t
                Q_hs_max_CL_d_t = Q_max_CL_d_t
                Q_hs_max_CS_d_t = Q_max_CS_d_t
            else:
                raise Exception('設備機器の種類の入力が不正です。')
            ####################################################################################################################

            # (20)　負荷バランス時の熱源機の入口における絶対湿度
            X_star_hs_in_d_t = dc.get_X_star_hs_in_d_t(X_star_NR_d_t)

            # (18)　熱源機の出口における空気温度の最低値
            X_hs_out_min_C_d_t = dc.get_X_hs_out_min_C_d_t(X_star_hs_in_d_t, Q_hs_max_CL_d_t, V_dash_supply_d_t_i)

            # (22)　熱源機の出口における要求絶対湿度
            X_req_d_t_i = dc.get_X_req_d_t_i(X_star_HBR_d_t, L_star_CL_d_t_i, V_dash_supply_d_t_i, region)

            # (21)　熱源機の出口における要求空気温度
            Theta_req_d_t_i = dc.get_Theta_req_d_t_i(Theta_sur_d_t_i, Theta_star_HBR_d_t, V_dash_supply_d_t_i,
                                L_star_H_d_t_i, L_star_CS_d_t_i, l_duct_i, region)

            if underfloor_air_conditioning_air_supply:
                for i in range(2):  # i=0,1
                    Theta_uf_d_t, Theta_g_surf_d_t, *others = \
                        uf.calc_Theta(
                            region, A_A, A_MR, A_OR, Q, YUCACO_r_A_ufvnt, underfloor_insulation,
                            Theta_req_d_t_i[i], Theta_ex_d_t, V_dash_supply_d_t_i[i],
                            '', L_H_d_t_i, L_CS_d_t_i, R_g)

                    if q_hs_rtd_H is not None:
                        mask = Theta_req_d_t_i[i] > Theta_uf_d_t
                    elif q_hs_rtd_C is not None:
                        mask = Theta_req_d_t_i[i] < Theta_uf_d_t
                    else:
                        raise IOError("冷房時・暖房時の判断に失敗しました。")

                    Theta_req_d_t_i[i] = np.where(mask,
                                                  Theta_req_d_t_i[i] + (Theta_req_d_t_i[i] - Theta_uf_d_t),
                                                  Theta_req_d_t_i[i])

            # TODO: ここに前時刻の非居室の温度を使用して負荷を下げる
            Theta_star_hs_in_d_t[t] = Theta_star_hs_in_d_t[0] if (isFirst or not (H[t] or C[t]))  \
                else Theta_NR_d_t[t-1]

            # NOTE: 過剰熱量繰越 未利用の場合では、式(14)(46)(48)の条件に合わせてTheta_NR_d_tを初期化
            # Theta_NR_d_t = np.zeros(24 * 365)
            # 過剰熱量繰越 利用時には、初期化せず再利用する

            # (15)　熱源機の出口における絶対湿度
            X_hs_out_d_t = dc.get_X_hs_out_d_t(X_NR_d_t, X_req_d_t_i, V_dash_supply_d_t_i, X_hs_out_min_C_d_t, L_star_CL_d_t_i, region)

            # (17)　冷房時の熱源機の出口における空気温度の最低値
            Theta_hs_out_min_C_d_t = dc.get_Theta_hs_out_min_C_d_t(Theta_star_hs_in_d_t, Q_hs_max_CS_d_t, V_dash_supply_d_t_i)

            # (16)　暖房時の熱源機の出口における空気温度の最高値
            Theta_hs_out_max_H_d_t = dc.get_Theta_hs_out_max_H_d_t(Theta_star_hs_in_d_t, Q_hs_max_H_d_t, V_dash_supply_d_t_i)

            # L_star_H_d_t_i，L_star_CS_d_t_iの暖冷房区画1～5を合算し0以上だった場合の順序で計算
            # (14)　熱源機の出口における空気温度
            Theta_hs_out_d_t = dc.get_Theta_hs_out_d_t(VAV, Theta_req_d_t_i, V_dash_supply_d_t_i,
                                                    L_star_H_d_t_i, L_star_CS_d_t_i, region, Theta_NR_d_t,
                                                    Theta_hs_out_max_H_d_t, Theta_hs_out_min_C_d_t)

            # (43)　暖冷房区画𝑖の吹き出し風量
            V_supply_d_t_i_before = dc.get_V_supply_d_t_i(L_star_H_d_t_i, L_star_CS_d_t_i, Theta_sur_d_t_i, l_duct_i, Theta_star_HBR_d_t,
                                                            V_vent_g_i, V_dash_supply_d_t_i, VAV, region, Theta_hs_out_d_t)
            V_supply_d_t_i = dc.cap_V_supply_d_t_i(V_supply_d_t_i_before, V_dash_supply_d_t_i, V_vent_g_i, region, V_hs_dsgn_H, V_hs_dsgn_C)

            # (41)　暖冷房区画𝑖の吹き出し温度
            Theta_supply_d_t_i = dc.get_Thata_supply_d_t_i(Theta_sur_d_t_i, Theta_hs_out_d_t, Theta_star_HBR_d_t, l_duct_i,
                                                       V_supply_d_t_i, L_star_H_d_t_i, L_star_CS_d_t_i, region)

            if underfloor_air_conditioning_air_supply:
                for i in range(2):  # i=0,1
                    Theta_uf_d_t, Theta_g_surf_d_t, *others = \
                        uf.calc_Theta(
                            region, A_A, A_MR, A_OR, Q, YUCACO_r_A_ufvnt, underfloor_insulation,
                            Theta_supply_d_t_i[i], Theta_ex_d_t, V_dash_supply_d_t_i[i],
                            '', L_H_d_t_i, L_CS_d_t_i, R_g)

                    if q_hs_rtd_H is not None:
                        mask = Theta_supply_d_t_i[i] > Theta_uf_d_t
                    elif q_hs_rtd_C is not None:
                        mask = Theta_supply_d_t_i[i] < Theta_uf_d_t
                    else:
                        raise IOError("冷房時・暖房時の判断に失敗しました。")

                    Theta_supply_d_t_i[i] = np.where(mask, Theta_uf_d_t, Theta_supply_d_t_i[i])

            # NOTE: t==0 でも最後までループを走ることに注意(途中で continue しない)
            # 0 の扱いは全てのメソッドで考慮されていること

            # (46)　暖冷房区画𝑖の実際の居室の室温
            Theta_HBR_d_t_i[:, t:t+1] \
                = jjj_carryover_heat.get_Theta_HBR_i_2023(
                    isFirst, H[t], C[t], M[t],
                    Theta_star_HBR_d_t[t],
                    V_supply_d_t_i[:, t:t+1],  # (5,1)
                    Theta_supply_d_t_i[:, t:t+1],  # (5,1)
                    U_prt,
                    A_prt_i.reshape(-1,1),  # (5,1)
                    Q,
                    A_HCZ_i.reshape(-1,1),  # (5,1)
                    L_star_H_d_t_i[:5, t:t+1],  # (5,1)
                    L_star_CS_d_t_i[:5, t:t+1],  # (5,1)
                    np.zeros((5,1)) if t==0 else Theta_HBR_d_t_i[:5, t-1:t])  # (5,1)

            # (48)　実際の非居室の室温
            Theta_NR_d_t[t] \
                = jjj_carryover_heat.get_Theta_NR_2023(
                    isFirst, H[t], C[t], M[t],
                    Theta_star_NR_d_t[t],
                    Theta_star_HBR_d_t[t],
                    Theta_HBR_d_t_i[:, t:t+1],  # (5,1)
                    A_NR,
                    V_vent_l_NR_d_t[t],
                    V_dash_supply_d_t_i[:, t:t+1],  # (5,1)
                    V_supply_d_t_i[:, t:t+1],  # (5,1)
                    U_prt,
                    A_prt_i.reshape(-1,1),  # (5,1)
                    Q,
                    0 if t==0 else Theta_NR_d_t[t-1])

    else:  # 過剰熱繰越ナシ(一般的なパターン)

        # NOTE: 床下空調のための r_A_ufvnt の上書きはココより前に行わない
        # 外気導入の負荷削減の計算までは、削減ナシ(r_A_ufvnt=None) のままであるべきため

        ''' r_A_ufac: 面積比 (空気供給室の床下面積 / 床下全体面積全体) [-]'''
        # NOTE: 以降では、r_A_ufvnt は床下空調ロジックのみに使用されているため、
        # 変数名を r_A_ufvnt -> r_A_ufac と変更して、統一して使用する

        check_variable_undefined("r_A_ufac")

        house_info = di.get(SampleHouseInfo)

        if constants.change_underfloor_temperature == 床下空調ロジック.変更する.value:
            # 床下空調 新ロジック
            r_A_ufac = 1.0  # WG資料に一致させるため
            house_info.r_A_ufac = r_A_ufac
        elif underfloor_air_conditioning_air_supply:
            # 床下空調 旧ロジック
            r_A_ufac = YUCACO_r_A_ufvnt  # (1.0 未満)
            house_info.r_A_ufac = r_A_ufac
            # NOTE: ユカコは新ロジックには使用しない ('24/02 先生)
        else:  # 非床下空調
            r_A_ufac = r_A_ufvnt
            house_info.r_A_ufac = r_A_ufac
        del r_A_ufvnt

        if constants.change_underfloor_temperature == 床下空調ロジック.変更する.value:
            # FIXME: 床下限定の数値だがとりあえず評価する L_star_の計算で不要なら無視されている
            # NOTE: 新ロジックでのみ 期待される床下温度を事前に計算(本計算は後で行う)
            Theta_uf_d_t_2023 = uf.calc_Theta_uf_d_t_2023(
                L_H_d_t_i, L_CS_d_t_i, A_A, A_MR, A_OR, r_A_ufac, V_dash_supply_d_t_i, Theta_ex_d_t)

            # (9')　熱取得を含む負荷バランス時の冷房顕熱負荷
            L_star_CS_d_t_i = \
                dc.get_L_star_newuf_CS_d_t_i(L_CS_d_t_i, Q_star_trs_prt_d_t_i, region,
                        A_A, A_MR, A_OR, Q, r_A_ufac, underfloor_insulation, Theta_uf_d_t_2023,
                        Theta_ex_d_t, V_dash_supply_d_t_i, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i, Theta_star_HBR_d_t, R_g, di)

            # (8')　熱損失を含む負荷バランス時の暖房負荷
            # 暖房負荷を補正する(暖房負荷 - 床下への損失 + 床下からの地盤への熱損失 + 床下から外気への熱損失)
            L_star_H_d_t_i, Theta_uf_supply_d_t = \
                dc.get_L_star_newuf_H_d_t_i(L_H_d_t_i, Q_star_trs_prt_d_t_i, region,
                        A_A, A_MR, A_OR, Q, r_A_ufac, underfloor_insulation, Theta_uf_d_t_2023,
                        Theta_ex_d_t, V_dash_supply_d_t_i, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i, Theta_star_HBR_d_t, R_g, di)

            # 床下空調 新ロジック 調査用出力ファイル
            survey_df_uf = di.get(UfVarsDataFrame)
            survey_df_uf.update_df({
                "L_H_d_t_1": L_H_d_t_i[0],   "L_H_d_t_2": L_H_d_t_i[1],   "L_H_d_t_3": L_H_d_t_i[2],   "L_H_d_t_4": L_H_d_t_i[3],   "L_H_d_t_5": L_H_d_t_i[4],
                "L_CS_d_t_1": L_CS_d_t_i[0], "L_CS_d_t_2": L_CS_d_t_i[1], "L_CS_d_t_3": L_CS_d_t_i[2], "L_CS_d_t_4": L_CS_d_t_i[3], "L_CS_d_t_5": L_CS_d_t_i[4],
                "L_CL_d_t_1": L_CL_d_t_i[0], "L_CL_d_t_2": L_CL_d_t_i[1], "L_CL_d_t_3": L_CL_d_t_i[2], "L_CL_d_t_4": L_CL_d_t_i[3], "L_CL_d_t_5": L_CL_d_t_i[4],
                "Theta_uf_d_t_2023": Theta_uf_d_t_2023,
                "L_star_CS_d_t_1": L_star_CS_d_t_i[0], "L_star_CS_d_t_2": L_star_CS_d_t_i[1], "L_star_CS_d_t_3": L_star_CS_d_t_i[2], "L_star_CS_d_t_4": L_star_CS_d_t_i[3], "L_star_CS_d_t_5": L_star_CS_d_t_i[4],
                "L_star_H_d_t_1":  L_star_H_d_t_i[0],  "L_star_H_d_t_2": L_star_H_d_t_i[1],   "L_star_H_d_t_3": L_star_H_d_t_i[2],   "L_star_H_d_t_4": L_star_H_d_t_i[3],   "L_star_H_d_t_5": L_star_H_d_t_i[4],
            })
        else:
            # (9)　熱取得を含む負荷バランス時の冷房顕熱負荷
            L_star_CS_d_t_i = dc.get_L_star_CS_d_t_i(L_CS_d_t_i, Q_star_trs_prt_d_t_i, region)
            # (8)　熱損失を含む負荷バランス時の暖房負荷
            L_star_H_d_t_i = dc.get_L_star_H_d_t_i(L_H_d_t_i, Q_star_trs_prt_d_t_i, region)

        ####################################################################################################################
        if type == PROCESS_TYPE_1 or type == PROCESS_TYPE_3:
            # (33)
            L_star_CL_d_t = dc.get_L_star_CL_d_t(L_star_CL_d_t_i)

            # (32)
            L_star_CS_d_t = dc.get_L_star_CS_d_t(L_star_CS_d_t_i)

            # (31)
            L_star_CL_max_d_t = dc.get_L_star_CL_max_d_t(L_star_CS_d_t)

            # (30)
            L_star_dash_CL_d_t = dc.get_L_star_dash_CL_d_t(L_star_CL_max_d_t, L_star_CL_d_t)

            # (29)
            L_star_dash_C_d_t = dc.get_L_star_dash_C_d_t(L_star_CS_d_t, L_star_dash_CL_d_t)

            # (28)
            SHF_dash_d_t = dc.get_SHF_dash_d_t(L_star_CS_d_t, L_star_dash_C_d_t)

            # (27)
            Q_hs_max_C_d_t = dc.get_Q_hs_max_C_d_t_2024(type, q_hs_rtd_C, input_C_af_C)

            # (26)
            Q_hs_max_CL_d_t = dc.get_Q_hs_max_CL_d_t(Q_hs_max_C_d_t, SHF_dash_d_t, L_star_dash_CL_d_t)

            # (25)
            Q_hs_max_CS_d_t = dc.get_Q_hs_max_CS_d_t(Q_hs_max_C_d_t, SHF_dash_d_t)

            # (24)
            C_df_H_d_t = dc.get_C_df_H_d_t(Theta_ex_d_t, h_ex_d_t)

            # (23)
            Q_hs_max_H_d_t = dc.get_Q_hs_max_H_d_t_2024(type, q_hs_rtd_H, C_df_H_d_t, input_C_af_H)

        elif type == PROCESS_TYPE_2 or type == PROCESS_TYPE_4:
            # (24)　デフロストに関する暖房出力補正係数
            C_df_H_d_t = dc.get_C_df_H_d_t(Theta_ex_d_t, h_ex_d_t)
            _logger.debug(f'C_df_H_d_t: {C_df_H_d_t}')

            # 最大暖房能力比
            q_r_max_H = rac.get_q_r_max_H(q_max_H, q_rtd_H)
            _logger.debug(f'q_r_max_H: {q_r_max_H}')  # here

            # 最大暖房出力比
            Q_r_max_H_d_t = rac.calc_Q_r_max_H_d_t(q_rtd_C, q_r_max_H, Theta_ex_d_t)
            _logger.NDdebug("Q_r_max_H_d_t", Q_r_max_H_d_t)  # here

            # 最大暖房出力
            Q_max_H_d_t = rac.calc_Q_max_H_d_t(Q_r_max_H_d_t, q_rtd_H, Theta_ex_d_t, h_ex_d_t, input_C_af_H)
            _logger.NDdebug("Q_max_H_d_t", Q_max_H_d_t)
            Q_hs_max_H_d_t = Q_max_H_d_t

            # 最大冷房能力比
            q_r_max_C = rac.get_q_r_max_C(q_max_C, q_rtd_C)
            _logger.debug(f"q_r_max_C: {q_r_max_C}")

            # 最大冷房出力比
            Q_r_max_C_d_t = rac.calc_Q_r_max_C_d_t(q_r_max_C, q_rtd_C, Theta_ex_d_t)
            _logger.NDdebug("Theta_ex_d_t", Theta_ex_d_t)
            _logger.NDdebug("Q_r_max_C_d_t", Q_r_max_C_d_t)

            # 最大冷房出力
            Q_max_C_d_t = rac.calc_Q_max_C_d_t(Q_r_max_C_d_t, q_rtd_C, input_C_af_C)
            _logger.NDdebug("Q_max_C_d_t", Q_max_C_d_t)
            Q_hs_max_C_d_t = Q_max_C_d_t

            # 冷房負荷最小顕熱比
            SHF_L_min_c = rac.get_SHF_L_min_c()

            # 最大冷房潜熱負荷
            L_max_CL_d_t = rac.get_L_max_CL_d_t(np.sum(L_CS_d_t_i, axis=0), SHF_L_min_c)

            # 補正冷房潜熱負荷
            L_dash_CL_d_t = rac.get_L_dash_CL_d_t(L_max_CL_d_t, np.sum(L_CL_d_t_i, axis=0))
            L_dash_C_d_t = rac.get_L_dash_C_d_t(np.sum(L_CS_d_t_i, axis=0), L_dash_CL_d_t)

            # 冷房負荷補正顕熱比
            SHF_dash_d_t = rac.get_SHF_dash_d_t(np.sum(L_CS_d_t_i, axis=0), L_dash_C_d_t)

            # 最大冷房顕熱出力, 最大冷房潜熱出力
            Q_max_CS_d_t = rac.get_Q_max_CS_d_t(Q_max_C_d_t, SHF_dash_d_t)
            Q_max_CL_d_t = rac.get_Q_max_CL_d_t(Q_max_C_d_t, SHF_dash_d_t, L_dash_CL_d_t)
            Q_hs_max_C_d_t = Q_max_C_d_t
            Q_hs_max_CL_d_t = Q_max_CL_d_t
            Q_hs_max_CS_d_t = Q_max_CS_d_t
        else:
            raise Exception('設備機器の種類の入力が不正です。')
        ####################################################################################################################

        # (20)　負荷バランス時の熱源機の入口における絶対湿度
        X_star_hs_in_d_t = dc.get_X_star_hs_in_d_t(X_star_NR_d_t)

        # (19)　負荷バランス時の熱源機の入口における空気温度
        Theta_star_hs_in_d_t = dc.get_Theta_star_hs_in_d_t(Theta_star_NR_d_t)

        # (18)　熱源機の出口における空気温度の最低値
        X_hs_out_min_C_d_t = dc.get_X_hs_out_min_C_d_t(X_star_hs_in_d_t, Q_hs_max_CL_d_t, V_dash_supply_d_t_i)

        # (22)　熱源機の出口における要求絶対湿度
        X_req_d_t_i = dc.get_X_req_d_t_i(X_star_HBR_d_t, L_star_CL_d_t_i, V_dash_supply_d_t_i, region)

        # (21)　熱源機の出口における要求空気温度
        Theta_req_d_t_i = dc.get_Theta_req_d_t_i(Theta_sur_d_t_i, Theta_star_HBR_d_t, V_dash_supply_d_t_i,
                            L_star_H_d_t_i, L_star_CS_d_t_i, l_duct_i, region)

        # NOTE: 床下空調を使用する(旧・新 両ロジックとも) 対象居室のみ損失分を補正する
        if constants.change_underfloor_temperature == 床下空調ロジック.変更する.value:
            assert Theta_uf_supply_d_t is not None, "1階居室の差替え用の床下温度が必要です"

            # 対象居室 i=1,2(1階居室)の損失分を補正する
            Theta_req_d_t_i = \
              np.vstack((np.tile(Theta_uf_supply_d_t, (2, 1)), Theta_req_d_t_i[2:, :]))
            assert np.shape(Theta_req_d_t_i)==(5, 8760), "想定外の行列数です"

            survey_df_uf = di.get(UfVarsDataFrame)
            survey_df_uf.update_df({
                "Theta_req_d_t_1": Theta_req_d_t_i[0], "Theta_req_d_t_2": Theta_req_d_t_i[1], "Theta_req_d_t_3": Theta_req_d_t_i[2], "Theta_req_d_t_4": Theta_req_d_t_i[3], "Theta_req_d_t_5": Theta_req_d_t_i[4],
            })
        elif underfloor_air_conditioning_air_supply == True:
            for i in range(2):  # 1F居室のみ(i=0,1)損失分を補正
                # CHECK: 床下温度が i(部屋) で変わるが問題ないか
                Theta_uf_d_t, Theta_g_surf_d_t, *others = \
                    uf.calc_Theta(
                        region, A_A, A_MR, A_OR, Q, r_A_ufac, underfloor_insulation,
                        Theta_req_d_t_i[i], Theta_ex_d_t, V_dash_supply_d_t_i[i],
                        '', L_H_d_t_i, L_CS_d_t_i, R_g)

                if q_hs_rtd_H is not None:  # 暖房
                  mask = Theta_req_d_t_i[i] > Theta_uf_d_t
                elif q_hs_rtd_C is not None:  # 冷房
                  mask = Theta_req_d_t_i[i] < Theta_uf_d_t
                else:
                    raise IOError("冷房時・暖房時の判断に失敗しました。")

                Theta_req_d_t_i[i] = np.where(mask,
                                            # 熱源機出口 -> 居室床下までの温度低下分を見込む
                                            Theta_req_d_t_i[i] + (Theta_req_d_t_i[i] - Theta_uf_d_t),
                                            Theta_req_d_t_i[i])
            assert np.shape(Theta_req_d_t_i)==(5, 8760), "想定外の行列数です"

        _logger.NDdebug("Theta_req_d_t_1", Theta_req_d_t_i[0])

        # (15)　熱源機の出口における絶対湿度
        X_hs_out_d_t = dc.get_X_hs_out_d_t(X_NR_d_t, X_req_d_t_i, V_dash_supply_d_t_i, X_hs_out_min_C_d_t, L_star_CL_d_t_i, region)

        # 式(14)(46)(48)の条件に合わせてTheta_NR_d_tを初期化
        Theta_NR_d_t = np.zeros(24 * 365)

        # (17)　冷房時の熱源機の出口における空気温度の最低値
        Theta_hs_out_min_C_d_t = dc.get_Theta_hs_out_min_C_d_t(Theta_star_hs_in_d_t, Q_hs_max_CS_d_t, V_dash_supply_d_t_i)

        # (16)　暖房時の熱源機の出口における空気温度の最高値
        Theta_hs_out_max_H_d_t = dc.get_Theta_hs_out_max_H_d_t(Theta_star_hs_in_d_t, Q_hs_max_H_d_t, V_dash_supply_d_t_i)

        # L_star_H_d_t_i，L_star_CS_d_t_iの暖冷房区画1～5を合算し0以上だった場合の順序で計算
        # (14)　熱源機の出口における空気温度
        Theta_hs_out_d_t = dc.get_Theta_hs_out_d_t(VAV, Theta_req_d_t_i, V_dash_supply_d_t_i,
                                                L_star_H_d_t_i, L_star_CS_d_t_i, region, Theta_NR_d_t,
                                                Theta_hs_out_max_H_d_t, Theta_hs_out_min_C_d_t)

        # (43)　暖冷房区画𝑖の吹き出し風量
        V_supply_d_t_i_before = dc.get_V_supply_d_t_i(L_star_H_d_t_i, L_star_CS_d_t_i, Theta_sur_d_t_i, l_duct_i, Theta_star_HBR_d_t,
                                                        V_vent_g_i, V_dash_supply_d_t_i, VAV, region, Theta_hs_out_d_t)
        V_supply_d_t_i = dc.cap_V_supply_d_t_i(V_supply_d_t_i_before, V_dash_supply_d_t_i, V_vent_g_i, region, V_hs_dsgn_H, V_hs_dsgn_C)

        # (41)　暖冷房区画𝑖の吹き出し温度
        Theta_supply_d_t_i = dc.get_Thata_supply_d_t_i(Theta_sur_d_t_i, Theta_hs_out_d_t, Theta_star_HBR_d_t, l_duct_i,
                                                       V_supply_d_t_i, L_star_H_d_t_i, L_star_CS_d_t_i, region)

        # 実行条件: 床下新空調ロジックのみ
        if constants.change_underfloor_temperature == 床下空調ロジック.変更する.value:
            # 熱源機出口温度から吹き出し温度を計算する
            V_sa_d_t = np.sum(V_dash_supply_d_t_i[:2, :], axis=0)  # i=1,2

            # i=1,2(1階居室)は床下を通して出口温度が中和されたものになる
            Theta_uf_d_t, *others = \
                uf.calc_Theta(
                    region, A_A, A_MR, A_OR, Q, r_A_ufac, underfloor_insulation,
                    Theta_hs_out_d_t,  # Theta_sa_d_t=
                    Theta_ex_d_t,
                    V_sa_d_t,  # V_sa_d_t_A=
                    '',  # H_OR_C=
                    L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i, R_g, di= None)
                    # NOTE: ここでは L_dash_/L_ の使い分けはあまり気にしない

            # CHECK: i=3,4,5(2階居室)は床下通さないので中和がなく高温なのは問題ないか
            # 床下・床上の熱貫流分だけ 目標床下温度からわずかな中和がある
            Theta_supply_d_t_i = \
                np.vstack((np.tile(Theta_uf_d_t, (2, 1)), Theta_supply_d_t_i[2:, :]))
            assert np.shape(Theta_supply_d_t_i)==(5, 8760), "想定外の行列数です"

            survey_df_uf = di.get(UfVarsDataFrame)
            survey_df_uf.update_df({
                "Theta_hs_out_d_t": Theta_hs_out_d_t,
                "Theta_supply_d_t_1": Theta_supply_d_t_i[0], "Theta_supply_d_t_2": Theta_supply_d_t_i[1], "Theta_supply_d_t_3": Theta_supply_d_t_i[2], "Theta_supply_d_t_4": Theta_supply_d_t_i[3], "Theta_supply_d_t_5": Theta_supply_d_t_i[4]
            })
        elif underfloor_air_conditioning_air_supply:
            for i in range(2):  #i=0,1
                Theta_uf_d_t, Theta_g_surf_d_t, *others = \
                    uf.calc_Theta(
                        region, A_A, A_MR, A_OR, Q, r_A_ufac, underfloor_insulation,
                        Theta_supply_d_t_i[i], Theta_ex_d_t, V_dash_supply_d_t_i[i],
                        '', L_H_d_t_i, L_CS_d_t_i, R_g)

                if q_hs_rtd_H is not None:  # 暖房
                    mask = Theta_supply_d_t_i[i] > Theta_uf_d_t
                elif q_hs_rtd_C is not None:  # 冷房
                    mask = Theta_supply_d_t_i[i] < Theta_uf_d_t
                else:
                    raise IOError("冷房時・暖房時の判断に失敗しました。")

                Theta_supply_d_t_i[i] = np.where(mask, Theta_uf_d_t, Theta_supply_d_t_i[i])

        if constants.change_underfloor_temperature == 床下空調ロジック.変更する.value:
            # (46')　暖冷房区画𝑖の実際の居室の室温
            Theta_HBR_d_t_i = dc.get_Theta_HBR_d_t_i(Theta_star_HBR_d_t, V_supply_d_t_i, Theta_supply_d_t_i, U_prt, A_prt_i, Q,
                                                     A_HCZ_i, L_star_H_d_t_i, L_star_CS_d_t_i, region,
                                                     r_A_ufac, A_A, A_MR, A_OR, Theta_uf_d_t)

            # (48')　実際の非居室の室温
            Theta_NR_d_t = dc.get_Theta_NR_d_t(Theta_star_NR_d_t, Theta_star_HBR_d_t, Theta_HBR_d_t_i, A_NR, V_vent_l_NR_d_t,
                                                V_dash_supply_d_t_i, V_supply_d_t_i, U_prt, A_prt_i, Q, Theta_uf_d_t, di=di)
        else:
            # (46)　暖冷房区画𝑖の実際の居室の室温
            Theta_HBR_d_t_i = dc.get_Theta_HBR_d_t_i(Theta_star_HBR_d_t, V_supply_d_t_i, Theta_supply_d_t_i, U_prt, A_prt_i, Q,
                                                     A_HCZ_i, L_star_H_d_t_i, L_star_CS_d_t_i, region,
                                                     r_A_ufac, A_A, A_MR, A_OR)

            # (48)　実際の非居室の室温
            Theta_NR_d_t = dc.get_Theta_NR_d_t(Theta_star_NR_d_t, Theta_star_HBR_d_t, Theta_HBR_d_t_i, A_NR, V_vent_l_NR_d_t,
                                                V_dash_supply_d_t_i, V_supply_d_t_i, U_prt, A_prt_i, Q, di=di)

    ### 熱繰越 / 非熱繰越 の分岐が終了 -> 以降、共通の処理 ###

    # NOTE: 繰越の有無によってCSV出力が異ならないよう df_output の処理は以降に限定する

    if constants.carry_over_heat == 過剰熱量繰越計算.行う.value:
        df_carryover_output = df_carryover_output.assign(
            carryovers_i_1 = carryovers[0],
            carryovers_i_2 = carryovers[1],
            carryovers_i_3 = carryovers[2],
            carryovers_i_4 = carryovers[3],
            carryovers_i_5 = carryovers[4]
        )
        if q_hs_rtd_H is not None and q_hs_rtd_C is None:
            df_carryover_output.to_csv(case_name + constants.version_info() + '_H_carryover_output.csv', encoding = 'cp932')
        elif q_hs_rtd_C is not None and q_hs_rtd_H is None:
            df_carryover_output.to_csv(case_name + constants.version_info() + '_C_carryover_output.csv', encoding = 'cp932')
        else:
            raise IOError("冷房時・暖房時の判断に失敗しました。")

    """ 熱損失・熱取得を含む負荷バランス時の熱負荷 - 熱損失・熱取得を含む負荷バランス時(2) """
    df_output = df_output.assign(
        L_star_CS_d_t_i_1 = L_star_CS_d_t_i[0],
        L_star_CS_d_t_i_2 = L_star_CS_d_t_i[1],
        L_star_CS_d_t_i_3 = L_star_CS_d_t_i[2],
        L_star_CS_d_t_i_4 = L_star_CS_d_t_i[3],
        L_star_CS_d_t_i_5 = L_star_CS_d_t_i[4]
    )
    df_output = df_output.assign(
        L_star_H_d_t_i_1 = L_star_H_d_t_i[0],
        L_star_H_d_t_i_2 = L_star_H_d_t_i[1],
        L_star_H_d_t_i_3 = L_star_H_d_t_i[2],
        L_star_H_d_t_i_4 = L_star_H_d_t_i[3],
        L_star_H_d_t_i_5 = L_star_H_d_t_i[4]
    )

    """ 最大暖冷房能力 """
    df_output = df_output.assign(
        # NOTE: タイプ毎に出力する変数の数を変えないようIFなどの分岐はしない
        # 以下タイプ(1, 3)
        L_star_CL_d_t = L_star_CL_d_t if "L_star_CL_d_t" in locals() else None,  # (33)
        L_star_CS_d_t = L_star_CS_d_t if "L_star_CS_d_t" in locals() else None,  # (32)
        L_star_dash_CL_d_t = L_star_dash_CL_d_t if "L_star_dash_CL_d_t" in locals() else None,  # (30)
        L_star_dash_C_d_t = L_star_dash_C_d_t if "L_star_dash_C_d_t" in locals() else None,   # (29)
        # 以下タイプ(2, 4)
        C_df_H_d_t = C_df_H_d_t if "C_df_H_d_t" in locals() else None,  # (24)
        Q_r_max_H_d_t = Q_r_max_H_d_t if "Q_r_max_H_d_t" in locals() else None,
        Q_r_max_C_d_t = Q_r_max_C_d_t if "Q_r_max_C_d_t" in locals() else None,
        L_max_CL_d_t = L_max_CL_d_t if "L_max_CL_d_t" in locals() else None,
        L_dash_CL_d_t = L_dash_CL_d_t if "L_dash_CL_d_t" in locals() else None,
        L_dash_C_d_t  = L_dash_C_d_t if "L_dash_C_d_t" in locals() else None,
    )
    df_output3 = df_output3.assign(
        # 以下タイプ(2, 4)
        q_r_max_H = q_r_max_H if "q_r_max_+H" in locals() else None,
        q_r_max_C = q_r_max_C if "q_r_max_C" in locals() else None,
        SHF_L_min_c = SHF_L_min_c if "SHF_L_min_c" in locals() else None,
    )
    df_output['SHF_dash_d_t'] = SHF_dash_d_t
    df_output = df_output.assign(
        Q_hs_max_C_d_t  = Q_hs_max_C_d_t,
        Q_hs_max_CL_d_t = Q_hs_max_CL_d_t,
        Q_hs_max_CS_d_t = Q_hs_max_CS_d_t,
        Q_hs_max_H_d_t  = Q_hs_max_H_d_t,
    )

    """ 熱源機の出口 - 負荷バランス時 """
    df_output['X_star_hs_in_d_t'] = X_star_hs_in_d_t
    df_output['Theta_star_hs_in_d_t'] = Theta_star_hs_in_d_t

    """ 熱源機の出口 - 熱源機の出口 """
    df_output['X_star_hs_in_d_t'] = X_star_hs_in_d_t
    df_output['Theta_star_hs_in_d_t'] = Theta_star_hs_in_d_t
    df_output['X_hs_out_min_C_d_t'] = X_hs_out_min_C_d_t
    df_output = df_output.assign(
        X_req_d_t_1 = X_req_d_t_i[0],
        X_req_d_t_2 = X_req_d_t_i[1],
        X_req_d_t_3 = X_req_d_t_i[2],
        X_req_d_t_4 = X_req_d_t_i[3],
        X_req_d_t_5 = X_req_d_t_i[4]
    )
    df_output = df_output.assign(
        Theta_req_d_t_1 = Theta_req_d_t_i[0],
        Theta_req_d_t_2 = Theta_req_d_t_i[1],
        Theta_req_d_t_3 = Theta_req_d_t_i[2],
        Theta_req_d_t_4 = Theta_req_d_t_i[3],
        Theta_req_d_t_5 = Theta_req_d_t_i[4]
    )
    df_output['X_hs_out_d_t'] = X_hs_out_d_t
    df_output = df_output.assign(
        Theta_hs_out_min_C_d_t = Theta_hs_out_min_C_d_t,
        Theta_hs_out_max_H_d_t = Theta_hs_out_max_H_d_t,
        Theta_hs_out_d_t = Theta_hs_out_d_t,
    )

    """吹出口 - 吹出口"""
    # NOTE: 2024/02/14 WG の話で出力してほしいデータになりました
    df_output = df_output.assign(
        V_supply_d_t_1_before = V_supply_d_t_i_before[0] if V_supply_d_t_i_before is not None else None,
        V_supply_d_t_2_before = V_supply_d_t_i_before[1] if V_supply_d_t_i_before is not None else None,
        V_supply_d_t_3_before = V_supply_d_t_i_before[2] if V_supply_d_t_i_before is not None else None,
        V_supply_d_t_4_before = V_supply_d_t_i_before[3] if V_supply_d_t_i_before is not None else None,
        V_supply_d_t_5_before = V_supply_d_t_i_before[4] if V_supply_d_t_i_before is not None else None,
    )
    df_output = df_output.assign(
        V_supply_d_t_1 = V_supply_d_t_i[0],
        V_supply_d_t_2 = V_supply_d_t_i[1],
        V_supply_d_t_3 = V_supply_d_t_i[2],
        V_supply_d_t_4 = V_supply_d_t_i[3],
        V_supply_d_t_5 = V_supply_d_t_i[4]
    )
    df_output = df_output.assign(
        Theta_supply_d_t_1 = Theta_supply_d_t_i[0],
        Theta_supply_d_t_2 = Theta_supply_d_t_i[1],
        Theta_supply_d_t_3 = Theta_supply_d_t_i[2],
        Theta_supply_d_t_4 = Theta_supply_d_t_i[3],
        Theta_supply_d_t_5 = Theta_supply_d_t_i[4]
    )

    """ 吹出口 - 実際 """
    df_output = df_output.assign(
        Theta_HBR_d_t_1 = Theta_HBR_d_t_i[0],
        Theta_HBR_d_t_2 = Theta_HBR_d_t_i[1],
        Theta_HBR_d_t_3 = Theta_HBR_d_t_i[2],
        Theta_HBR_d_t_4 = Theta_HBR_d_t_i[3],
        Theta_HBR_d_t_5 = Theta_HBR_d_t_i[4],
        Theta_NR_d_t = Theta_NR_d_t
    )

    """ 吹出口 - 熱源機の出口 """
    # L_star_H_d_t_i，L_star_CS_d_t_iの暖冷房区画1～5を合算し0以下だった場合の為に再計算
    # (14)　熱源機の出口における空気温度
    Theta_hs_out_d_t = dc.get_Theta_hs_out_d_t(VAV, Theta_req_d_t_i, V_dash_supply_d_t_i,
                                            L_star_H_d_t_i, L_star_CS_d_t_i, region, Theta_NR_d_t,
                                            Theta_hs_out_max_H_d_t, Theta_hs_out_min_C_d_t)
    df_output['Theta_hs_out_d_t'] = Theta_hs_out_d_t

    """ 吹出口 - 吹出口 """
    # (42)　暖冷房区画𝑖の吹き出し絶対湿度
    X_supply_d_t_i = dc.get_X_supply_d_t_i(X_star_HBR_d_t, X_hs_out_d_t, L_star_CL_d_t_i, region)
    df_output = df_output.assign(
        X_supply_d_t_1 = X_supply_d_t_i[0],
        X_supply_d_t_2 = X_supply_d_t_i[1],
        X_supply_d_t_3 = X_supply_d_t_i[2],
        X_supply_d_t_4 = X_supply_d_t_i[3],
        X_supply_d_t_5 = X_supply_d_t_i[4]
    )

    """ 熱源機の入口 - 熱源機の風量の計算 """
    # (35)　熱源機の風量のうちの全般換気分
    V_hs_vent_d_t = dc.get_V_hs_vent_d_t(V_vent_g_i, general_ventilation)
    df_output['V_hs_vent_d_t'] = V_hs_vent_d_t

    # (34)　熱源機の風量
    V_hs_supply_d_t = dc.get_V_hs_supply_d_t(V_supply_d_t_i)
    df_output['V_hs_supply_d_t'] = V_hs_supply_d_t

    """ 熱源機の入口 - 熱源機の入口 """
    # (13)　熱源機の入口における絶対湿度
    X_hs_in_d_t = dc.get_X_hs_in_d_t(X_NR_d_t)
    df_output['X_hs_in_d_t'] = X_hs_in_d_t

    # (12)　熱源機の入口における空気温度
    Theta_hs_in_d_t = dc.get_Theta_hs_in_d_t(Theta_NR_d_t)
    df_output['Theta_hs_in_d_t'] = Theta_hs_in_d_t

    """ まとめ - 実際の暖冷房負荷 """
    # (7)　間仕切りの熱取得を含む実際の冷房潜熱負荷
    L_dash_CL_d_t_i = dc.get_L_dash_CL_d_t_i(V_supply_d_t_i, X_HBR_d_t_i, X_supply_d_t_i, region)
    df_output = df_output.assign(
        L_dash_CL_d_t_1 = L_dash_CL_d_t_i[0],
        L_dash_CL_d_t_2 = L_dash_CL_d_t_i[1],
        L_dash_CL_d_t_3 = L_dash_CL_d_t_i[2],
        L_dash_CL_d_t_4 = L_dash_CL_d_t_i[3],
        L_dash_CL_d_t_5 = L_dash_CL_d_t_i[4]
    )
    # (6)　間仕切りの熱取得を含む実際の冷房顕熱負荷
    L_dash_CS_d_t_i = dc.get_L_dash_CS_d_t_i(V_supply_d_t_i, Theta_supply_d_t_i, Theta_HBR_d_t_i, region)
    df_output = df_output.assign(
        L_dash_CS_d_t_1 = L_dash_CS_d_t_i[0],
        L_dash_CS_d_t_2 = L_dash_CS_d_t_i[1],
        L_dash_CS_d_t_3 = L_dash_CS_d_t_i[2],
        L_dash_CS_d_t_4 = L_dash_CS_d_t_i[3],
        L_dash_CS_d_t_5 = L_dash_CS_d_t_i[4]
    )
    # (5)　間仕切りの熱損失を含む実際の暖房負荷
    L_dash_H_d_t_i = dc.get_L_dash_H_d_t_i(V_supply_d_t_i, Theta_supply_d_t_i, Theta_HBR_d_t_i, region)
    df_output = df_output.assign(
        L_dash_H_d_t_1 = L_dash_H_d_t_i[0],
        L_dash_H_d_t_2 = L_dash_H_d_t_i[1],
        L_dash_H_d_t_3 = L_dash_H_d_t_i[2],
        L_dash_H_d_t_4 = L_dash_H_d_t_i[3],
        L_dash_H_d_t_5 = L_dash_H_d_t_i[4]
    )

    """ まとめ - 未処理負荷 """
    # (4)　冷房設備機器の未処理冷房潜熱負荷
    Q_UT_CL_d_t_i = dc.get_Q_UT_CL_d_t_i(L_star_CL_d_t_i, L_dash_CL_d_t_i)
    df_output = df_output.assign(
        Q_UT_CL_d_t_1 = Q_UT_CL_d_t_i[0],
        Q_UT_CL_d_t_2 = Q_UT_CL_d_t_i[1],
        Q_UT_CL_d_t_3 = Q_UT_CL_d_t_i[2],
        Q_UT_CL_d_t_4 = Q_UT_CL_d_t_i[3],
        Q_UT_CL_d_t_5 = Q_UT_CL_d_t_i[4]
    )
    # (3)　冷房設備機器の未処理冷房顕熱負荷
    Q_UT_CS_d_t_i = dc.get_Q_UT_CS_d_t_i(L_star_CS_d_t_i, L_dash_CS_d_t_i)
    df_output = df_output.assign(
        Q_UT_CS_d_t_1 = Q_UT_CS_d_t_i[0],
        Q_UT_CS_d_t_2 = Q_UT_CS_d_t_i[1],
        Q_UT_CS_d_t_3 = Q_UT_CS_d_t_i[2],
        Q_UT_CS_d_t_4 = Q_UT_CS_d_t_i[3],
        Q_UT_CS_d_t_5 = Q_UT_CS_d_t_i[4]
    )
    # (2)　暖房設備機器等の未処理暖房負荷
    Q_UT_H_d_t_i = dc.get_Q_UT_H_d_t_i(L_star_H_d_t_i, L_dash_H_d_t_i)
    df_output = df_output.assign(
        Q_UT_H_d_t_1 = Q_UT_H_d_t_i[0],
        Q_UT_H_d_t_2 = Q_UT_H_d_t_i[1],
        Q_UT_H_d_t_3 = Q_UT_H_d_t_i[2],
        Q_UT_H_d_t_4 = Q_UT_H_d_t_i[3],
        Q_UT_H_d_t_5 = Q_UT_H_d_t_i[4]
    )

    """ まとめ - 一次エネルギー """
    # (1)　冷房設備の未処理冷房負荷の設計一次エネルギー消費量相当値
    E_C_UT_d_t = dc.get_E_C_UT_d_t(Q_UT_CL_d_t_i, Q_UT_CS_d_t_i, region)
    df_output['E_C_UT_d_t'] = E_C_UT_d_t

    # 床下空調新ロジック調査用変数の出力
    if constants.change_underfloor_temperature == 床下空調ロジック.変更する.value:
        hci = di.get(HaCaInputHolder)
        filename = case_name + constants.version_info() + hci.flg_char() + "_output_uf.csv"
        survey_df_uf = di.get(UfVarsDataFrame)  # ネスト関数内で更新されているデータフレーム
        survey_df_uf.export_to_csv(filename)

    if q_hs_rtd_H is not None:
        df_output3.to_csv(case_name + constants.version_info() + '_H_output3.csv', encoding = 'cp932')
        df_output2.to_csv(case_name + constants.version_info() + '_H_output4.csv', encoding = 'cp932')
        df_output.to_csv(case_name  + constants.version_info() + '_H_output5.csv', encoding = 'cp932')
    else:
        df_output3.to_csv(case_name + constants.version_info() + '_C_output3.csv', encoding = 'cp932')
        df_output2.to_csv(case_name + constants.version_info() + '_C_output4.csv', encoding = 'cp932')
        df_output.to_csv(case_name  + constants.version_info() + '_C_output5.csv', encoding = 'cp932')

    return E_C_UT_d_t, Q_UT_H_d_t_i, Q_UT_CS_d_t_i, Q_UT_CL_d_t_i, Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t, \
           X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, V_hs_vent_d_t, C_df_H_d_t
