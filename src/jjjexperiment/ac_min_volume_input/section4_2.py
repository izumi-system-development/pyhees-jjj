import numpy as np

import pyhees.section4_2 as dc
# JJJ
from jjjexperiment.common import *
import jjjexperiment.constants as jjj_consts
from jjjexperiment.options import *

def get_V_hs_min(
        q_hs_rtd_H: float,
        q_hs_rtd_C: float,
        V_vent_g_i: Array5
    ) -> float:
    """(39)-改変 熱源機の最低風量

    Args:
        q_hs_rtd_H: 定格暖房能力 (HC判別) [kW]
        q_hs_rtd_C: 定格冷房能力 (HC判別) [kW]
        V_vent_g_i: 暖冷房区画iの全般換気量 [m3/h]
    Returns:
        熱源機の最低風量 [m3/h]

    """
    # 暖房時/冷房時で異なるユーザー入力を使用する
    match(q_hs_rtd_H, q_hs_rtd_C):
        case(None, None):
            raise Exception('q_hs_rtd_H, q_hs_rtd_C はどちらかのみを前提としています')
        case(_, None):  # 暖房時
            # CHECK: フラグの個別化
            if jjj_consts.input_V_hs_min == 最低風量直接入力.入力する.value:
                V_hs_min = jjj_consts.V_hs_min_H
            else:
                V_hs_min = dc.get_V_hs_min(V_vent_g_i)  # 従来式
        case(None, _):  # 冷房時
            # CHECK: フラグの個別化
            if jjj_consts.input_V_hs_min == 最低風量直接入力.入力する.value:
                V_hs_min = jjj_consts.V_hs_min_C
            else:
                V_hs_min = dc.get_V_hs_min(V_vent_g_i)  # 従来式
        case(_, _):
            raise Exception('q_hs_rtd_H, q_hs_rtd_C はどちらかのみを前提としています')
    return V_hs_min

def get_V_hs_vent_d_t(
        region: int,
        V_vent_g_i: Array5,
        general_ventilation: bool,
        input_V_hs_min: bool
    ) -> Array8760:
    """(35-1)(35-2) 改造版

    Args:
        region: 地域区分
        V_vent_g_i: 暖冷房区画iの全般換気量 [m3/h]
        general_ventilation: 全版換気の機能
        input_V_hs_min: 最低風量直接入力の有無

    Returns:
        日付dの時刻tにおける 熱源機の風量のうちの全般換気分 [m3/h]

    """
    H, C, _ = dc.get_season_array_d_t(region)

    # NOTE: 下記ロジックより暖房冷房どちらか片方のみの最低風量入力はコントロールが困難なため
    # どちらか片方でも最低風量入力がある場合は、本ロジックを使用する

    # 全般換気の機能を有する場合
    if general_ventilation == True:
        if input_V_hs_min == 最低風量直接入力.入力する.value:  # 最低風量直接入力あり
            V_vent_g = np.sum(V_vent_g_i[:5])
            V_hs_vent_d_t = np.ones(24 * 365) * V_vent_g
            V_hs_vent_d_t[H & (V_vent_g < jjj_consts.V_hs_min_H)] \
                = jjj_consts.V_hs_min_H
            V_hs_vent_d_t[C & (V_vent_g < jjj_consts.V_hs_min_C)] \
                = jjj_consts.V_hs_min_C
        else:  # 最低風量直接入力なし
            # デフォルト条件 -> オリジナルのまま
            V_hs_vent_d_t = dc.get_V_hs_vent_d_t(V_vent_g_i, general_ventilation)

    # 全般換気の機能を有さない場合
    elif general_ventilation == False:
        if input_V_hs_min == 最低風量直接入力.入力する.value:  # 最低風量直接入力あり
            V_hs_vent_d_t = np.zeros(24 * 365)
            V_hs_vent_d_t[H] = jjj_consts.V_hs_min_H
            V_hs_vent_d_t[C] = jjj_consts.V_hs_min_C
        else:  # 最低風量直接入力なし
            # オリジナルのまま
            V_hs_vent_d_t = dc.get_V_hs_vent_d_t(V_vent_g_i, general_ventilation)

    else:
        raise ValueError(general_ventilation)

    return V_hs_vent_d_t
