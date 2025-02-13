import numpy as np
from nptyping import NDArray, Float64, Shape

import pyhees.section4_2 as dc
# JJJ
import jjjexperiment.constants as constants
from jjjexperiment.options import *

def get_V_hs_vent_d_t(
        region: int,
        V_vent_g_i: NDArray[Shape['5'], Float64],
        general_ventilation: bool,
        input_V_hs_min: bool
    ) -> NDArray[Shape['8760'], Float64]:
    """(35-1)(35-2) 改造版

    Args:
        region: 地域区分
        V_vent_g_i: 暖冷房区画iの全般換気量 [m3/h]
        general_ventilation: 全版換気の機能
        input_V_hs_min: 最低風量直接入力の有無

    Returns:
        日付dの時刻tにおける 熱源機の風量のうちの全般換気分 [m3/h]

    """
    H, C, M = dc.get_season_array_d_t(region)
    mask = np.logical_or(H, C)

    # NOTE: 下記ロジックより暖房冷房どちらか片方のみの最低風量入力はコントロールが困難なため
    # どちらか片方でも最低風量入力がある場合は、本ロジックを使用する

    # 全般換気の機能を有する場合
    if general_ventilation == True:
        if input_V_hs_min == 最低風量直接入力.入力する.value:  # 最低風量直接入力あり
            V_vent_g = np.sum(V_vent_g_i[:5])
            V_hs_vent_d_t = np.ones(24 * 365) * V_vent_g
            V_hs_vent_d_t[H & (V_vent_g < constants.V_hs_min_H)] \
                = constants.V_hs_min_H
            V_hs_vent_d_t[C & (V_vent_g < constants.V_hs_min_C)] \
                = constants.V_hs_min_C
        else:  # 最低風量直接入力なし
            # オリジナルそのまま
            V_hs_vent_d_t = dc.get_V_hs_vent_d_t(V_vent_g_i, general_ventilation)

    # 全般換気の機能を有さない場合
    elif general_ventilation == False:
        if input_V_hs_min == 最低風量直接入力.入力する.value:  # 最低風量直接入力あり
            V_hs_vent_d_t = np.zeros(24 * 365)
            V_hs_vent_d_t[H] = constants.V_hs_min_H
            V_hs_vent_d_t[C] = constants.V_hs_min_C
        else:  # 最低風量直接入力なし
            # オリジナル
            V_hs_vent_d_t = dc.get_V_hs_vent_d_t(V_vent_g_i, general_ventilation)
            # JJJ
            # WARNING: 既存の結果の多くに影響を与える
            # V_hs_vent_d_t[mask] = np.sum(V_vent_g_i[:5])

    else:
        raise ValueError(general_ventilation)

    return V_hs_vent_d_t
