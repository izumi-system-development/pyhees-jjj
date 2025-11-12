import numpy as np

import pyhees.section3_1 as ld
import pyhees.section3_2 as gihi
import pyhees.section4_2 as dc
import pyhees.section4_2_b as dc_spec
# JJJ
from jjjexperiment.common import *
from jjjexperiment.inputs.common import HouseInfo, OuterSkin

class EnvironmentEntity:

    def __init__(self, house: HouseInfo, skin: OuterSkin):
        self._skin = skin
        self._house = house

    def get_A_NR(self) -> float:
        return ld.get_A_NR(self._house.A_A, self._house.A_MR, self._house.A_OR)

    def get_mu_H(self) -> float:
        mu_H = gihi.get_mu_H(self._skin.eta_A_H, self._skin.r_env)
        return mu_H

    def get_mu_C(self) -> float:
        mu_C = gihi.get_mu_C(self._skin.eta_A_C, self._skin.r_env)
        return mu_C

    def get_A_HCZ_i(self) -> Array12:
        return np.array([
            ld.get_A_HCZ_i(i, self._house.A_A, self._house.A_MR, self._house.A_OR) \
            for i in range(1, 13)
        ])

    def get_A_HCZ_R_i(self) -> Array12:
        return np.array([ld.get_A_HCZ_R_i(i) for i in range(1, 13)])

    def get_V_vent_g_i(self) -> Array5:
        # (62) 全般換気量
        A_HCZ_i = [ld.get_A_HCZ_i(i, self._house.A_A, self._house.A_MR, self._house.A_OR) for i in range(1, 6)]
        A_HCZ_R_i = [ld.get_A_HCZ_R_i(i) for i in range(1, 6)]
        V_vent_g_i = dc.get_V_vent_g_i(A_HCZ_i, A_HCZ_R_i)
        return np.array(V_vent_g_i)

    def get_V_vent_l_NR_d_t(self) -> Array8760:
        # (63) 局所排気量
        V_vent_l_NR_d_t = dc.get_V_vent_l_NR_d_t()
        return V_vent_l_NR_d_t

    def get_q_gen_d_t(self) -> Array8760:
        A_NR = ld.get_A_NR(self._house.A_A, self._house.A_MR, self._house.A_OR)
        # (64d) 非居室の内部発熱
        q_gen_NR_d_t = dc.calc_q_gen_NR_d_t(A_NR)
        # (64c) その他居室の内部発熱
        q_gen_OR_d_t = dc.calc_q_gen_OR_d_t(self._house.A_OR)
        # (64b) 主たる居室の内部発熱
        q_gen_MR_d_t = dc.calc_q_gen_MR_d_t(self._house.A_MR)
        # (64a) 内部発熱
        q_gen_d_t = dc.get_q_gen_d_t(q_gen_NR_d_t, q_gen_OR_d_t, q_gen_MR_d_t)
        return q_gen_d_t

    def get_n_p_d_t(self) -> Array8760:
        A_NR = ld.get_A_NR(self._house.A_A, self._house.A_MR, self._house.A_OR)
        # (66d) 非居室の在室人数
        n_p_NR_d_t = dc.calc_n_p_NR_d_t(A_NR)
        # (66c) その他居室の在室人数
        n_p_OR_d_t = dc.calc_n_p_OR_d_t(self._house.A_OR)
        # (66b) 主たる居室の在室人数
        n_p_MR_d_t = dc.calc_n_p_MR_d_t(self._house.A_MR)
        # (66a) 在室人数
        n_p_d_t = dc.get_n_p_d_t(n_p_NR_d_t, n_p_OR_d_t, n_p_MR_d_t)
        return n_p_d_t

    def get_w_gen_d_t(self) -> Array8760:
        A_NR = ld.get_A_NR(self._house.A_A, self._house.A_MR, self._house.A_OR)
        # (65d) 非居室の内部発湿
        w_gen_NR_d_t = dc.calc_w_gen_NR_d_t(A_NR)
        # (65c) その他居室の内部発湿
        w_gen_OR_d_t = dc.calc_w_gen_OR_d_t(self._house.A_OR)
        # (65b) 主たる居室の内部発湿
        w_gen_MR_d_t = dc.calc_w_gen_MR_d_t(self._house.A_MR)
        # (65a) 内部発湿
        w_gen_d_t = dc.get_w_gen_d_t(w_gen_NR_d_t, w_gen_OR_d_t, w_gen_MR_d_t)
        return w_gen_d_t

    def get_Q(self) -> float:
        # (1) 熱損失係数(換気による熱損失を含まない)
        Q_dash = gihi.get_Q_dash(self._skin.U_A, self._skin.r_env)
        # (15) 熱損失係数
        Q = ld.get_Q(Q_dash)
        return Q
