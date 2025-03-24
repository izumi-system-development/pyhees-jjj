import numpy as np
from typing import Any

import pyhees.section3_1_e as algo
import pyhees.section4_2 as dc
import pyhees.section4_2_b as dc_spec
import pyhees.section11_1 as rgn
import pyhees.section11_2 as slr
# JJJ
from jjjexperiment.common import *
from jjjexperiment.inputs import jjj_ipt

class ArgHEntity:
    """ region に関するデータを保持するクラス """

    def __init__(self, input: jjj_ipt.InputDto):
        self._input = input
        self.proc_type = self.process_type(self._input.H_A.type)
        self.prepare_spec()

    def process_type(self, type_flg: int) -> JJJ_PROC_TYPE:
        match type_flg:
            case JJJ_PROC_TYPE.ダクト式セントラル空調機.value:
                return JJJ_PROC_TYPE.ダクト式セントラル空調機

            case JJJ_PROC_TYPE.RAC活用型全館空調_現行省エネ法RACモデル.value:
                return JJJ_PROC_TYPE.RAC活用型全館空調_現行省エネ法RACモデル

            case JJJ_PROC_TYPE.RAC活用型全館空調_潜熱評価モデル.value:
                return JJJ_PROC_TYPE.RAC活用型全館空調_潜熱評価モデル

            case JJJ_PROC_TYPE.電中研モデル.value:
                return JJJ_PROC_TYPE.電中研モデル

            case _:
                raise ValueError('type_flg is invalid')

    def prepare_spec(self) -> None:
        self.equipment_spec: JJJ_SpecInput  \
            = JJJ_SpecInput(self._input.H_A.input)

        # NOTE: (q) => (P), (q) => (V), (V) => (P)

        # 定格能力試験の値
        if self._input.H_A.input == 1:
            self.q_hs_rtd_H = dc_spec.get_q_hs_rtd_H(self._input.region, self._input.A_A)
            self.P_hs_rtd_H = dc_spec.get_P_hs_rtd_H(self.q_hs_rtd_H)
            self.V_fan_rtd_H = dc_spec.get_V_fan_rtd_H(self.q_hs_rtd_H)
            self.P_fan_rtd_H = dc_spec.get_P_fan_rtd_H(self.V_fan_rtd_H)
        elif self._input.H_A.input == 2 or self._input.H_A.input == 3:
            self.q_hs_rtd_H = self._input.H_A.q_hs_rtd_H
            self.P_hs_rtd_H = self._input.H_A.P_hs_rtd_H
            self.V_fan_rtd_H = self._input.H_A.V_fan_rtd_H
            self.P_fan_rtd_H = self._input.H_A.P_fan_rtd_H
        else:
            pass

        self.q_hs_min_H = dc_spec.get_q_hs_min_H(self.q_hs_rtd_H)
        # 中間能力試験の値
        if self._input.H_A.input == 1 or self._input.H_A.input == 2:
            self.q_hs_mid_H = dc_spec.get_q_hs_mid_H(self.q_hs_rtd_H)
            self.V_fan_mid_H = dc_spec.get_V_fan_mid_H(self.q_hs_mid_H)
            self.P_fan_mid_H = dc_spec.get_P_fan_mid_H(self.V_fan_mid_H)
            self.P_hs_mid_H = None  # 未使用らしい
        elif self._input.H_A.input == 3:
            self.q_hs_mid_H = self._input.H_A.q_hs_mid_H
            self.V_fan_mid_H = self._input.H_A.V_fan_mid_H
            self.P_fan_mid_H = self._input.H_A.P_fan_mid_H
            self.P_hs_mid_H = self._input.H_A.P_hs_mid_H
        else:
            pass

        if self._input.H_A.input == 4:  # CHECK: 有効かどうか確認が必要
            self.q_rac_min_H = self._input.H_A.q_rac_min_H
            self.q_rac_rtd_H = self._input.H_A.q_rac_rtd_H
            self.q_rac_max_H = self._input.H_A.q_rac_max_H
            self.P_rac_min_H = self._input.H_A.P_rac_min_H
            self.P_rac_rtd_H = self._input.H_A.P_rac_rtd_H
            self.P_rac_max_H = self._input.H_A.P_rac_max_H
            self.V_rac_inner_H = self._input.H_A.V_rac_inner_H
            self.V_rac_outer_H = self._input.H_A.V_rac_outer_H
            self.Theta_RH_rac_inner_pub_H = self._input.H_A.Theta_RH_rac_inner_pub_H
            self.Theta_RH_rac_outer_pub_H = self._input.H_A.Theta_RH_rac_outer_pub_H
            self.RH_rac_inner_pub_H = self._input.H_A.RH_rac_inner_pub_H
            self.RH_rac_outer_pub_H = self._input.H_A.RH_rac_outer_pub_H
        else:
            pass


    # Inputから直接V_hs_dsgn_H取得せずこちら使用する
    def get_V_hs_dsgn_H(
            self, q_rtd_H: float = 0
            ) -> tuple[float, None]:
        """(V_hs_dsgn_H, V_hs_dsgn_C=None)
        暖房時の設計風量
        Args:
            q_rtd_H: 暖房時の定格能力 (W)
        Returns:
            tuple(float, None):
                - V_hs_dsgn_H: 暖房時の設計風量 (m3/h)
                - V_hs_dsgn_C: 冷房時の設計風量 (m3/h)
        """
        if self._input.H_A.input_V_hs_dsgn_H == 2:
            return self._input.H_A.V_hs_dsgn_H

        assert q_rtd_H is not None
        match self.proc_type:
            case JJJ_PROC_TYPE.ダクト式セントラル空調機:
                assert self.V_fan_rtd_H is not None
                V_fan_rtd_H = self.V_fan_rtd_H
            case JJJ_PROC_TYPE.RAC活用型全館空調_潜熱評価モデル:
                assert self.V_fan_rtd_H is not None
                V_fan_rtd_H = self.V_fan_rtd_H

            case JJJ_PROC_TYPE.RAC活用型全館空調_現行省エネ法RACモデル:
                assert q_rtd_H != 0
                V_fan_rtd_H = dc_spec.get_V_fan_rtd_H(q_rtd_H)
            case JJJ_PROC_TYPE.電中研モデル:
                assert q_rtd_H != 0
                V_fan_rtd_H = dc_spec.get_V_fan_rtd_H(q_rtd_H)

            case _:
                raise ValueError('type is invalid')

        # 暖房負荷計算時は、冷房風量はなしとなる
        return dc_spec.get_V_fan_dsgn_H(V_fan_rtd_H), None
