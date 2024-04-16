import numpy as np
import pyhees.section4_2_b as dc_spec
import pyhees.section4_3_a as rac_spec

from jjjexperiment.constants import PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_3, PROCESS_TYPE_4
import jjjexperiment.constants as constants

from jjjexperiment.denchu_1 import Spec, Condition, absolute_humid
from jjjexperiment.options import *

def get_basic(input: dict):
    """ 基本情報の設定

    Returns:
    (住宅タイプ, 住宅建て方, 床面積, 面積の合計[m2], 主たる居室の面積[m2], その他の居室の面積[m2], 地域区分, 年間日射地域区分)

    """
    # 住宅タイプ
    type = '一般住宅'

    # 住宅建て方
    tatekata = '戸建住宅'

    # 床面積
    A_A = float(input['A_A'])
    A_MR = float(input['A_MR'])
    A_OR = float(input['A_OR'])

    # 地域区分
    region = int(input['region'])

    # 年間日射地域区分
    sol_region = None

    return type, tatekata, A_A, A_MR, A_OR, region, sol_region

def get_env(input: dict):
    """外皮の設定

    :return: 外皮条件
    """
    ENV = {
        'method': '当該住宅の外皮面積の合計を用いて評価する',
        'A_env': float(input['A_env']),
        'A_A': float(input['A_A']),
        'U_A': float(input['U_A']),
        'eta_A_H': float(input['eta_A_H']),
        'eta_A_C': float(input['eta_A_C'])
    }

    # 自然風の利用 主たる居室
    NV_MR = 0
    # 自然風の利用 その他居室
    NV_OR = 0

    # 蓄熱
    TS = False

    # 床下空間を経由して外気を導入する換気方式の利用
    if input['underfloor_ventilation'] == '2':
        r_A_ufvnt = float(input['r_A_ufvnt']) / 100
    else:
        r_A_ufvnt = None
    # NOTE: 床下空調アリの時には r_A_ufvnt の代わりに YUCACO_r_A_ufvnt が使用される

    # 床下空間の断熱
    underfloor_insulation = int(input['underfloor_insulation']) == 2
    # 空調空気を床下を通して給気する
    underfloor_air_conditioning_air_supply = int(input['underfloor_air_conditioning_air_supply']) == 2

    # NOTE: 床下空調ロジック「変更する」を優先して強制的に床下空調アリの状態にします
    if constants.change_underfloor_temperature == 床下空調ロジック.変更する.value:
        underfloor_air_conditioning_air_supply = True

    if underfloor_air_conditioning_air_supply:
        print("床下空調がオンです。強制的に、床下換気ナシ・床下断熱状態となります。")
        underfloor_insulation = True

    # 全体風量を固定する
    hs_CAV = input['hs_CAV'] == '2'

    return ENV, NV_MR, NV_OR, TS, r_A_ufvnt, underfloor_insulation, underfloor_air_conditioning_air_supply, hs_CAV

def get_rac_catalog_spec(input: dict, TH_FC: bool):
    """ 電中研モデル計算時に使用するメーカー公表のルームエアコン仕様
    Inputs:
        TH_FC: True->H or False->C
    Return:
        spec: ルームエアコンのカタログスペック \n
        condition: カタログスペック計測時の使用環境(基本はJIS指定値) \n
        T_real_inner [℃]: 実際の使用状況におけるエアコン吸込み空気の 温度 \n
        RH_real_inner [%]: 実際の使用状況におけるエアコン吸込み空気の 相対温度 \n
    """
    i = input['H_A'] if TH_FC else input['C_A']
    spec = Spec(
        i['P_rac_pub_min'], i['P_rac_pub_rtd'], i['P_rac_pub_max'],
        i['q_rac_pub_min'], i['q_rac_pub_rtd'], i['q_rac_pub_max'],
        i['V_rac_pub_inner'], i['V_rac_pub_outer'])

    """ 温熱環境条件 JIS """
    t_ein = i["Theta_rac_pub_outer"] if TH_FC else i["Theta_rac_pub_inner"]
    t_cin = i["Theta_rac_pub_inner"] if TH_FC else i["Theta_rac_pub_outer"]

    """ 温熱環境条件 実測値 """
    t_real_inner  = i["Theta_rac_real_inner"]
    rh_real_inner = i["RH_rac_real_inner"]

    cdtn = Condition(
        T_ein = t_ein,
        T_cin = t_cin,
        X_ein = absolute_humid(i["RH_rac_pub_outer"] if TH_FC else i["RH_rac_pub_inner"], t_ein),
        X_cin = absolute_humid(i["RH_rac_pub_inner"] if TH_FC else i["RH_rac_pub_outer"], t_cin))
    return spec, cdtn, t_real_inner, rh_real_inner

def get_heating(input: dict, region: int, A_A: float):
    """暖房の設定

    :return: 暖房方式、住戸全体の暖房条件、主たる居室の暖房機器、その他居室の暖房機器、温水暖房の種類
    """
    # 暖房方式
    mode_H = '住戸全体を連続的に暖房する方式'

    H_A = {
        'VAV': int(input['H_A']['VAV']) == 2,
        'general_ventilation': int(input['H_A']['general_ventilation']) == 1,
    }

    # ファンの比消費電力（暖房）
    if int(input['H_A']['input_f_SFP_H']) == 2:
        H_A['f_SFP_H'] = float(input['H_A']['f_SFP_H'])
    else:
        H_A['f_SFP_H'] = 0.4 * 0.36

    # 暖房設備機器の種類
    if int(input['H_A']['type']) == 1:
        H_A['type'] = PROCESS_TYPE_1
    elif int(input['H_A']['type']) == 2:
        H_A['type'] = PROCESS_TYPE_2
    elif int(input['H_A']['type']) == 3:
        H_A['type'] = PROCESS_TYPE_3
    elif int(input['H_A']['type']) == 4:
        H_A['type'] = PROCESS_TYPE_4
    else:
        raise Exception('暖房設備機器の種類の入力が不正です。')

    # ダクトが通過する空間
    if input['H_A']['duct_insulation'] == '全てもしくは一部が断熱区画外である' or int(input['H_A']['duct_insulation']) == 1:
        H_A['duct_insulation'] = '全てもしくは一部が断熱区画外である'
    elif str(input['H_A']['duct_insulation']) == '全て断熱区画内である' or int(input['H_A']['duct_insulation']) == 2:
        H_A['duct_insulation'] = '全て断熱区画内である'
    else:
        raise Exception('ダクトが通過する空間の入力が不正です。')

    # 機器の仕様の入力（section4_1.calc_E_E_H_hs_A_d_t()から引用）
    if int(input['H_A']['input']) == 1:
        H_A['EquipmentSpec'] = '入力しない'
        H_A['q_hs_rtd_H'] = dc_spec.get_q_hs_rtd_H(region, A_A)
        H_A['q_hs_mid_H'] = dc_spec.get_q_hs_mid_H(H_A['q_hs_rtd_H'])
        H_A['q_hs_min_H'] = dc_spec.get_q_hs_min_H(H_A['q_hs_rtd_H'])
        H_A['P_hs_rtd_H'] = dc_spec.get_P_hs_rtd_H(H_A['q_hs_rtd_H'])
        H_A['V_fan_rtd_H'] = dc_spec.get_V_fan_rtd_H(H_A['q_hs_rtd_H'])
        H_A['V_fan_mid_H'] = dc_spec.get_V_fan_mid_H(H_A['q_hs_mid_H'])
        H_A['P_fan_rtd_H'] = dc_spec.get_P_fan_rtd_H(H_A['V_fan_rtd_H'])
        H_A['P_fan_mid_H'] = dc_spec.get_P_fan_mid_H(H_A['V_fan_mid_H'])
        H_A['P_hs_mid_H'] = np.NAN
    elif int(input['H_A']['input']) == 2:
        H_A['EquipmentSpec'] = '定格能力試験の値を入力する'
        H_A['q_hs_rtd_H'] = float(input['H_A']['q_hs_rtd_H'])
        H_A['P_hs_rtd_H'] = float(input['H_A']['P_hs_rtd_H'])
        H_A['V_fan_rtd_H'] = float(input['H_A']['V_fan_rtd_H'])
        H_A['P_fan_rtd_H'] = float(input['H_A']['P_fan_rtd_H'])
        H_A['q_hs_mid_H'] = dc_spec.get_q_hs_mid_H(H_A['q_hs_rtd_H'])
        H_A['q_hs_min_H'] = dc_spec.get_q_hs_min_H(H_A['q_hs_rtd_H'])
        H_A['V_fan_mid_H'] = dc_spec.get_V_fan_mid_H(H_A['q_hs_mid_H'])
        H_A['P_fan_mid_H'] = dc_spec.get_P_fan_mid_H(H_A['V_fan_mid_H'])
        H_A['P_hs_mid_H'] = np.NAN
    elif int(input['H_A']['input']) == 3:
        H_A['EquipmentSpec'] = '定格能力試験と中間能力試験の値を入力する'
        H_A['q_hs_rtd_H'] = float(input['H_A']['q_hs_rtd_H'])
        H_A['P_hs_rtd_H'] = float(input['H_A']['P_hs_rtd_H'])
        H_A['V_fan_rtd_H'] = float(input['H_A']['V_fan_rtd_H'])
        H_A['P_fan_rtd_H'] = float(input['H_A']['P_fan_rtd_H'])
        H_A['q_hs_mid_H'] = float(input['H_A']['q_hs_mid_H'])
        H_A['P_hs_mid_H'] = float(input['H_A']['P_hs_mid_H'])
        H_A['V_fan_mid_H'] = float(input['H_A']['V_fan_mid_H'])
        H_A['P_fan_mid_H'] = float(input['H_A']['P_fan_mid_H'])
        H_A['q_hs_min_H'] = dc_spec.get_q_hs_min_H(H_A['q_hs_rtd_H'])
    elif int(input['H_A']['input']) == 4:
        # WARNING: このケースは存在しますか?
        H_A['EquipmentSpec'] = '最小・定格・最大出力時のメーカー公表値を入力する'
        H_A['q_rac_min_H']   = float(input['H_A']['q_rac_min_H'])
        H_A['q_rac_rtd_H']   = float(input['H_A']['q_rac_rtd_H'])
        H_A['q_rac_max_H']   = float(input['H_A']['q_rac_max_H'])
        H_A['P_rac_min_H']   = float(input['H_A']['P_rac_min_H'])
        H_A['P_rac_rtd_H']   = float(input['H_A']['P_rac_rtd_H'])
        H_A['P_rac_max_H']   = float(input['H_A']['P_rac_max_H'])
        H_A['V_rac_inner_H'] = float(input['H_A']['V_rac_inner_H'])
        H_A['V_rac_outer_H'] = float(input['H_A']['V_rac_outer_H'])
        H_A['Theta_RH_rac_inner_pub_H'] = float(input['H_A']['Theta_RH_rac_inner_pub_H'])
        H_A['Theta_RH_rac_outer_pub_H'] = float(input['H_A']['Theta_RH_rac_outer_pub_H'])
        H_A['RH_rac_inner_pub_H']       = float(input['H_A']['RH_rac_inner_pub_H'])
        H_A['RH_rac_outer_pub_H']       = float(input['H_A']['RH_rac_outer_pub_H'])
    else:
        raise Exception('機器の仕様の入力が不正です。')

    # 設計風量
    if int(input['H_A']['input_V_hs_dsgn_H']) == 2:
        H_A['V_hs_dsgn_H'] = float(input['H_A']['V_hs_dsgn_H'])

    # 主たる居室暖房機器
    H_MR = None

    # その他居室暖房機器
    H_OR = None

    # 温水暖房機の種類
    H_HS = None

    return mode_H, H_A, H_MR, H_OR, H_HS

def get_cooling(input: dict, region: int, A_A: float):
    """冷房の設定

    :return: 冷房方式、住戸全体の冷房条件、主たる居室冷房条件、その他居室冷房条件
    """
    # 冷房方式
    mode_C = '住戸全体を連続的に冷房する方式'

    C_A = {
        'VAV': int(input['C_A']['VAV']) == 2,
        'general_ventilation': int(input['C_A']['general_ventilation']) == 1,
    }

    # ファンの比消費電力（冷房）
    if int(input['C_A']['input_f_SFP_C']) == 2:
        C_A['f_SFP_C'] = float(input['C_A']['f_SFP_C'])
    else:
        C_A['f_SFP_C'] = 0.4 * 0.36

    # 冷房設備機器の種類
    if int(input['C_A']['type']) == 1:
        C_A['type'] = PROCESS_TYPE_1
    elif int(input['C_A']['type']) == 2:
        C_A['type'] = PROCESS_TYPE_2
    elif int(input['C_A']['type']) == 3:
        C_A['type'] = PROCESS_TYPE_3
    elif int(input['C_A']['type']) == 4:
        C_A['type'] = PROCESS_TYPE_4
    else:
        raise Exception('冷房設備機器の種類の入力が不正です。')

    # ダクトが通過する空間
    if str(input['C_A']['duct_insulation']) == '全てもしくは一部が断熱区画外である' or int(input['C_A']['duct_insulation']) == 1:
        C_A['duct_insulation'] = '全てもしくは一部が断熱区画外である'
    elif str(input['C_A']['duct_insulation']) == '全て断熱区画内である' or int(input['C_A']['duct_insulation']) == 2:
        C_A['duct_insulation'] = '全て断熱区画内である'
    else:
        raise Exception('ダクトが通過する空間の入力が不正です。')

    # 機器の仕様の入力（section4_1.calc_E_E_C_hs_d_t()から引用）
    if int(input['C_A']['input']) == 1:
        C_A['EquipmentSpec'] = '入力しない'
        C_A['q_hs_rtd_C'] = dc_spec.get_q_hs_rtd_C(region, A_A)
        C_A['q_hs_mid_C'] = dc_spec.get_q_hs_mid_C(C_A['q_hs_rtd_C'])
        C_A['q_hs_min_C'] = dc_spec.get_q_hs_min_C(C_A['q_hs_rtd_C'])
        C_A['P_hs_rtd_C'] = dc_spec.get_P_hs_rtd_C(C_A['q_hs_rtd_C'])
        C_A['V_fan_rtd_C'] = dc_spec.get_V_fan_rtd_C(C_A['q_hs_rtd_C'])
        C_A['V_fan_mid_C'] = dc_spec.get_V_fan_mid_C(C_A['q_hs_mid_C'])
        C_A['P_fan_rtd_C'] = dc_spec.get_P_fan_rtd_C(C_A['V_fan_rtd_C'])
        C_A['P_fan_mid_C'] = dc_spec.get_P_fan_mid_C(C_A['V_fan_mid_C'])
        C_A['P_hs_mid_C'] = np.NAN
    elif int(input['C_A']['input']) == 2:
        C_A['EquipmentSpec'] = '定格能力試験の値を入力する'
        C_A['q_hs_rtd_C'] = float(input['C_A']['q_hs_rtd_C'])
        C_A['P_hs_rtd_C'] = float(input['C_A']['P_hs_rtd_C'])
        C_A['V_fan_rtd_C'] = float(input['C_A']['V_fan_rtd_C'])
        C_A['P_fan_rtd_C'] = float(input['C_A']['P_fan_rtd_C'])
        C_A['q_hs_mid_C'] = dc_spec.get_q_hs_mid_C(C_A['q_hs_rtd_C'])
        C_A['q_hs_min_C'] = dc_spec.get_q_hs_min_C(C_A['q_hs_rtd_C'])
        C_A['V_fan_mid_C'] = dc_spec.get_V_fan_mid_C(C_A['q_hs_mid_C'])
        C_A['P_fan_mid_C'] = dc_spec.get_P_fan_mid_C(C_A['V_fan_mid_C'])
        C_A['P_hs_mid_C'] = np.NAN
    elif int(input['C_A']['input']) == 3:
        C_A['EquipmentSpec'] = '定格能力試験と中間能力試験の値を入力する'
        C_A['q_hs_rtd_C'] = float(input['C_A']['q_hs_rtd_C'])
        C_A['P_hs_rtd_C'] = float(input['C_A']['P_hs_rtd_C'])
        C_A['V_fan_rtd_C'] = float(input['C_A']['V_fan_rtd_C'])
        C_A['P_fan_rtd_C'] = float(input['C_A']['P_fan_rtd_C'])
        C_A['q_hs_mid_C'] = float(input['C_A']['q_hs_mid_C'])
        C_A['P_hs_mid_C'] = float(input['C_A']['P_hs_mid_C'])
        C_A['V_fan_mid_C'] = float(input['C_A']['V_fan_mid_C'])
        C_A['P_fan_mid_C'] = float(input['C_A']['P_fan_mid_C'])
        C_A['q_hs_min_C'] = dc_spec.get_q_hs_min_C(C_A['q_hs_rtd_C'])
    elif int(input['C_A']['input']) == 4:
        # WARNING: このケースは存在しますか?
        C_A['EquipmentSpec'] = '最小・定格・最大出力時のメーカー公表値を入力する'
        C_A['q_rac_min_C']   = float(input['C_A']['q_rac_min_C'])
        C_A['q_rac_rtd_C']   = float(input['C_A']['q_rac_rtd_C'])
        C_A['q_rac_max_C']   = float(input['C_A']['q_rac_max_C'])
        C_A['P_rac_min_C']   = float(input['C_A']['P_rac_min_C'])
        C_A['P_rac_rtd_C']   = float(input['C_A']['P_rac_rtd_C'])
        C_A['P_rac_max_C']   = float(input['C_A']['P_rac_max_C'])
        C_A['V_rac_inner_C'] = float(input['C_A']['V_rac_inner_C'])
        C_A['V_rac_outer_C'] = float(input['C_A']['V_rac_outer_C'])
        C_A['Theta_RH_rac_inner_pub_C'] = float(input['C_A']['Theta_RH_rac_inner_pub_C'])
        C_A['Theta_RH_rac_outer_pub_C'] = float(input['C_A']['Theta_RH_rac_outer_pub_C'])
        C_A['RH_rac_inner_pub_C']       = float(input['C_A']['RH_rac_inner_pub_C'])
        C_A['RH_rac_outer_pub_C']       = float(input['C_A']['RH_rac_outer_pub_C'])
    else:
        raise Exception('機器の仕様の入力が不正です。')

    # 設計風量
    if int(input['C_A']['input_V_hs_dsgn_C']) == 2:
        C_A['V_hs_dsgn_C'] = float(input['C_A']['V_hs_dsgn_C'])

    # 主たる居室冷房機器
    C_MR = None

    # その他居室冷房機器
    C_OR = None

    return mode_C, C_A, C_MR, C_OR

def get_CRAC_spec(input: dict):
    # エネルギー消費効率の入力（冷房）
    # 暖房の当該入力項目は使われない
    e_class = None
    if int(input['C_A']['input_mode']) == 2:
        if int(input['C_A']['mode']) == 1:
            e_class = 'い'
        elif int(input['C_A']['mode']) == 2:
            e_class = 'ろ'
        elif int(input['C_A']['mode']) == 3:
            e_class = 'は'
        else:
            raise Exception('エネルギー消費効率の入力（冷房）が不正です。')

    # 機器の性能の入力(冷房) [W]で統一する
    if input['C_A']['type'] == 2 and int(input['C_A']['input_rac_performance']) == 2:
        q_rtd_C: float = float(input['C_A']['q_rac_rtd_C'])
        q_max_C: float = float(input['C_A']['q_rac_max_C'])
        e_rtd_C: float = float(input['C_A']['e_rac_rtd_C'])
    elif input['C_A']['type'] == 4:
        q_rtd_C: float = float(input['C_A']['q_rac_pub_rtd']) * 1000
        q_max_C: float = float(input['C_A']['q_rac_pub_max']) * 1000
        e_rtd_C: float = rac_spec.get_e_rtd_C(e_class, q_rtd_C)
    else:  # 全形式のデフォルト
        q_rtd_C: float = rac_spec.get_q_rtd_C(input['A_A'])
        q_max_C: float = rac_spec.get_q_max_C(q_rtd_C)
        e_rtd_C: float = rac_spec.get_e_rtd_C(e_class, q_rtd_C)

    # 機器の性能の入力(暖房) [W]で統一する
    if input['H_A']['type'] == 2 and int(input['H_A']['input_rac_performance']) == 2:
        q_rtd_H: float = float(input['H_A']['q_rac_rtd_H'])
        q_max_H: float = float(input['H_A']['q_rac_max_H'])
        e_rtd_H: float = float(input['H_A']['e_rac_rtd_H'])
    elif input['H_A']['type'] == 4:
        q_rtd_H: float = float(input['H_A']['q_rac_pub_rtd']) * 1000
        q_max_H: float = float(input['H_A']['q_rac_pub_max']) * 1000
        e_rtd_H: float = rac_spec.get_e_rtd_H(e_rtd_C)
    else:
        q_rtd_H: float = rac_spec.get_q_rtd_H(q_rtd_C)
        q_max_H: float = rac_spec.get_q_max_H(q_rtd_H, q_max_C)
        e_rtd_H: float = rac_spec.get_e_rtd_H(e_rtd_C)

    # 小能力時高効率型コンプレッサー
    dualcompressor_C: bool = int(input['C_A']['dualcompressor']) == 2 if input['C_A']['type'] == 2 else None
    dualcompressor_H: bool = int(input['H_A']['dualcompressor']) == 2 if input['H_A']['type'] == 2 else None

    # NOTE: 方式2 以外でも評価されていたので全体適用としました
    # 室内機吹き出し風量に関する出力補正係数の入力（冷房）
    # 方式ごとに入力項目があるため、typeを見て取得する値を変えます。
    # 方式1はルームエアコンでないため、入力がありません。
    input_C_af_C: dict = {
        'input_mode': 2,
        'dedicated_chamber': False,
        'fixed_fin_direction': False,
        'C_af_C': 1.0
    }
    if input['C_A']['type'] == 2:
        input_C_af_C['input_mode'] = int(input['C_A']['input_C_af_C2'])
        input_C_af_C['dedicated_chamber'] = int(input['C_A']['dedicated_chamber2']) == 2
        input_C_af_C['fixed_fin_direction'] = int(input['C_A']['fixed_fin_direction2']) == 2
        input_C_af_C['C_af_C'] = float(input['C_A']['C_af_C2']) if input_C_af_C['input_mode'] == 2 else None
    elif input['C_A']['type'] == 3:
        input_C_af_C['input_mode'] = int(input['C_A']['input_C_af_C3'])
        input_C_af_C['dedicated_chamber'] = int(input['C_A']['dedicated_chamber3']) == 2
        input_C_af_C['fixed_fin_direction'] = int(input['C_A']['fixed_fin_direction3']) == 2
        input_C_af_C['C_af_C'] = float(input['C_A']['C_af_C3']) if input_C_af_C['input_mode'] == 2 else None
    elif input['C_A']['type'] == 4:
        input_C_af_C['input_mode'] = int(input['C_A']['input_C_af_C4'])
        input_C_af_C['dedicated_chamber'] = int(input['C_A']['dedicated_chamber4']) == 2
        input_C_af_C['fixed_fin_direction'] = int(input['C_A']['fixed_fin_direction4']) == 2
        input_C_af_C['C_af_C'] = float(input['C_A']['C_af_C4']) if input_C_af_C['input_mode'] == 2 else None

    # 室内機吹き出し風量に関する出力補正係数の入力（暖房）
    input_C_af_H: dict = {
        'input_mode': 2,
        'dedicated_chamber': False,
        'fixed_fin_direction': False,
        'C_af_H': 1.0
    }
    if input['H_A']['type'] == 2:
        input_C_af_H['input_mode'] = int(input['H_A']['input_C_af_H2'])
        input_C_af_H['dedicated_chamber'] = int(input['H_A']['dedicated_chamber2']) == 2
        input_C_af_H['fixed_fin_direction'] = int(input['H_A']['fixed_fin_direction2']) == 2
        input_C_af_H['C_af_H'] = float(input['H_A']['C_af_H2']) if input_C_af_H['input_mode'] == 2 else None
    elif input['H_A']['type'] == 3:
        input_C_af_H['input_mode'] = int(input['H_A']['input_C_af_H3'])
        input_C_af_H['dedicated_chamber'] = int(input['H_A']['dedicated_chamber3']) == 2
        input_C_af_H['fixed_fin_direction'] = int(input['H_A']['fixed_fin_direction3']) == 2
        input_C_af_H['C_af_H'] = float(input['H_A']['C_af_H3']) if input_C_af_H['input_mode'] == 2 else None
    elif input['H_A']['type'] == 4:
        input_C_af_H['input_mode'] = int(input['H_A']['input_C_af_H4'])
        input_C_af_H['dedicated_chamber'] = int(input['H_A']['dedicated_chamber4']) == 2
        input_C_af_H['fixed_fin_direction'] = int(input['H_A']['fixed_fin_direction4']) == 2
        input_C_af_H['C_af_H'] = float(input['H_A']['C_af_H4']) if input_C_af_H['input_mode'] == 2 else None

    return q_rtd_C, q_rtd_H, q_max_C, q_max_H, e_rtd_C, e_rtd_H, dualcompressor_C, dualcompressor_H, \
        input_C_af_C, input_C_af_H

def get_heatexchangeventilation(input: dict):
    """熱交換型換気の設定

    :return: 熱交換型換気
    """

    if int(input['HEX']['install']) == 1:
        # 熱交換型換気
        HEX = None
    else:
        HEX = {
            'hex':      True,
            'etr_t':    input['HEX']['etr_t'],      #温度交換効率
            'e_bal':    0.9,                        #給気と排気の比率による温度交換効率の補正係数
            'e_leak':   1.0                         #排気過多時における住宅外皮経由の漏気による温度交換効率の補正係数
        }

    return HEX

def get_solarheat():
    """太陽熱利用の設定

    :return: 太陽熱利用
    """
    # 太陽熱利用
    SHC = None

    return SHC
