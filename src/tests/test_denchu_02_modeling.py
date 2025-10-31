import pytest
import math

from jjjexperiment.denchu_1 import *
from jjjexperiment.denchu.denchu_2 import *

from jjjexperiment.logger import LimitedLoggerAdapter as _logger

""" 論文におけるエアコンの性能 """

ronbun_spec_hi_C = Spec(
    name = "論文-高機能機-冷房",
    q_rac_min = 0.7,
    q_rac_rtd = 2.2,
    q_rac_max = 3.3,
    P_rac_min = 95,
    P_rac_rtd = 395,
    P_rac_max = 780,
    V_inner = 12.1,
    V_outer = 28.2)

ronbun_spec_cmm_C = Spec(
    name = "論文-普及機-冷房",
    q_rac_min = 0.9,
    q_rac_rtd = 2.2,
    q_rac_max = 2.8,
    P_rac_min = 170,
    P_rac_rtd = 455,
    P_rac_max = 745,
    V_inner = 12.0,
    V_outer = 27.6)

ronbun_spec_hi_H = Spec(
    name = "論文-高機能機-暖房",
    q_rac_min = 0.7,
    q_rac_rtd = 2.5,
    q_rac_max = 5.4,
    P_rac_min = 95,
    P_rac_rtd = 395,
    P_rac_max = 1360,
    V_inner = 13.1,
    V_outer = 25.5)

ronbun_spec_cmm_H = Spec(
    name = "論文-普及機-暖房",
    q_rac_min = 0.9,
    q_rac_rtd = 2.2,
    q_rac_max = 3.6,
    P_rac_min = 135,
    P_rac_rtd = 385,
    P_rac_max = 1070,
    V_inner = 12.0,
    V_outer = 22.5)

""" 論文におけるエアコンの使用条件 """

# エアコン吸込空気温度(JIS利用条件)
t_inner_C = 27
t_outer_C = 35
t_outer_H = 7
t_inner_H = 20

# 相対湿度[%] 論文掲載値から計算
rh_inner_C = 46.6
rh_outer_C = 40.0
rh_inner_H = 58.6
rh_outer_H = 86.7

# 使用条件 - 冷房時
ronbun_cdtn_C = Condition(
    T_ein = t_inner_C,
    T_cin = t_outer_C,
    X_ein = absolute_humid(rh_inner_C, t_inner_C),
    X_cin = absolute_humid(rh_outer_C, t_outer_C))

# 使用条件 - 暖房時 (evp, cnd が逆になります)
ronbun_cdtn_H = Condition(
    T_ein = t_outer_H,
    T_cin = t_inner_H,
    X_ein = absolute_humid(rh_outer_H, t_outer_H),
    X_cin = absolute_humid(rh_inner_H, t_inner_H))


class Test成績係数比R_モデリング:

    def test_論文計算再現_高機能機_冷房(self):
        """ 論文のR近似式が再現できることを確認
        """
        a2, a1, a0, Pc = calc_R_and_Pc_C(ronbun_spec_hi_C, ronbun_cdtn_C)

        R_sut = simu_R(a2, a1, a0)
        R1_sut = R_sut(ronbun_spec_hi_C.q_rac_min)
        R2_sut = R_sut(ronbun_spec_hi_C.q_rac_rtd)
        R3_sut = R_sut(ronbun_spec_hi_C.q_rac_max)

        R = simu_R(-0.018, 0.052, 0.513)  # 論文より
        R1 = R(ronbun_spec_hi_C.q_rac_min)
        R2 = R(ronbun_spec_hi_C.q_rac_rtd)
        R3 = R(ronbun_spec_hi_C.q_rac_max)

        assert math.isclose(R1, R1_sut, abs_tol=1e-2)
        assert math.isclose(R2, R2_sut, abs_tol=1e-2)
        assert math.isclose(R3, R3_sut, abs_tol=1e-2)

    def test_論文計算再現_普及機_冷房(self):
        """ 論文のR近似式が再現できることを確認
        """
        a2, a1, a0, Pc = calc_R_and_Pc_C(ronbun_spec_cmm_C, ronbun_cdtn_C)

        R_sut = simu_R(a2, a1, a0)
        R1_sut = R_sut(ronbun_spec_cmm_C.q_rac_min)
        R2_sut = R_sut(ronbun_spec_cmm_C.q_rac_rtd)
        R3_sut = R_sut(ronbun_spec_cmm_C.q_rac_max)

        R = simu_R(-0.082, 0.255, 0.365)  # 論文より
        R1 = R(ronbun_spec_cmm_C.q_rac_min)
        R2 = R(ronbun_spec_cmm_C.q_rac_rtd)
        R3 = R(ronbun_spec_cmm_C.q_rac_max)

        assert math.isclose(R1, R1_sut, abs_tol=1e-2)
        assert math.isclose(R2, R2_sut, abs_tol=1e-2)
        assert math.isclose(R3, R3_sut, abs_tol=1e-2)

    def test_論文計算再現_高機能機_暖房(self):
        """ 論文のR近似式が再現できることを確認
        """
        a2, a1, a0, Pc = calc_R_and_Pc_H(ronbun_spec_hi_H, ronbun_cdtn_H)

        R_sut = simu_R(a2, a1, a0)
        R1_sut = R_sut(ronbun_spec_hi_H.q_rac_min)
        R2_sut = R_sut(ronbun_spec_hi_H.q_rac_rtd)
        R3_sut = R_sut(ronbun_spec_hi_H.q_rac_max)

        R = simu_R(-0.006, 0.019, 0.636)  # 論文より
        R1 = R(ronbun_spec_hi_H.q_rac_min)
        R2 = R(ronbun_spec_hi_H.q_rac_rtd)
        R3 = R(ronbun_spec_hi_H.q_rac_max)

        assert math.isclose(R1, R1_sut, abs_tol=2e-2)  # FIXME: 精度?
        assert math.isclose(R2, R2_sut, abs_tol=2e-2)  # FIXME: 精度?
        assert math.isclose(R3, R3_sut, abs_tol=1e-2)

    def test_論文計算再現_普及機_暖房(self):
        """ 論文のR近似式が再現できることを確認
        """
        a2, a1, a0, Pc = calc_R_and_Pc_H(ronbun_spec_cmm_H, ronbun_cdtn_H)

        R_sut = simu_R(a2, a1, a0)
        R1_sut = R_sut(ronbun_spec_cmm_C.q_rac_min)
        R2_sut = R_sut(ronbun_spec_cmm_C.q_rac_rtd)
        R3_sut = R_sut(ronbun_spec_cmm_C.q_rac_max)

        R = simu_R(-0.044, 0.136, 0.479)  # 論文より
        R1 = R(ronbun_spec_cmm_C.q_rac_min)
        R2 = R(ronbun_spec_cmm_C.q_rac_rtd)
        R3 = R(ronbun_spec_cmm_C.q_rac_max)

        assert math.isclose(R1, R1_sut, abs_tol=1e-2)
        assert math.isclose(R2, R2_sut, abs_tol=1e-2)
        assert math.isclose(R3, R3_sut, abs_tol=1e-2)
