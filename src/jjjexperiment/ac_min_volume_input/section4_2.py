import numpy as np

import pyhees.section4_2 as dc
# JJJ
from jjjexperiment.common import *
from jjjexperiment.inputs.options import *
from jjjexperiment.inputs.app_config import *

def get_V_hs_min_H(V_vent_g_i: Array5) -> float:
    return get_V_hs_min(1, None, V_vent_g_i)

def get_V_hs_min_C(V_vent_g_i: Array5) -> float:
    return get_V_hs_min(None, 1, V_vent_g_i)

@jjj_cloning
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
    app_config = injector.get(AppConfig)

    match(q_hs_rtd_H, q_hs_rtd_C):
        case(None, None):
            raise Exception('q_hs_rtd_H, q_hs_rtd_C はどちらかのみを前提としています')

        case(_, None):  # 暖房時
            # CHECK: フラグの個別化
            if app_config.H.input_V_hs_min == 最低風量直接入力.入力する.value:
                V_hs_min = app_config.H.V_hs_min
            else:
                V_hs_min = dc.get_V_hs_min(V_vent_g_i)  # 従来式

        case(None, _):  # 冷房時
            # CHECK: フラグの個別化
            if app_config.C.input_V_hs_min == 最低風量直接入力.入力する.value:
                V_hs_min = app_config.C.V_hs_min
            else:
                V_hs_min = dc.get_V_hs_min(V_vent_g_i)  # 従来式

        case(_, _):
            raise Exception('q_hs_rtd_H, q_hs_rtd_C はどちらかのみを前提としています')
    return V_hs_min

