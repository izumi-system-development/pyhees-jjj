import pytest
import math

from jjjexperiment.denchu_1 import *
from jjjexperiment.denchu.denchu_2 import *

from jjjexperiment.logger import LimitedLoggerAdapter as _logger

""" R近似曲線とPcの算出後 -> 使用条件実情でCOP値推計 """

R_ronbun_C = simu_R(-0.018, 0.052, 0.513)
Pc_ronbun_C = 0.0361  # kW

R_ronbun_H = simu_R(-0.006, 0.019, 0.636)
Pc_ronbun_H = 0.0303  # kW
# TODO: 暖房時のCOP推計結果が論文になくテストできません

""" 実際の使用条件(論文から転記) """

# 使用時の風量[m3/min]
v_inner = 12.1
v_outer = 28.2

# エアコン吸込空気温度
t_inner_C = 27
t_outer_C = None  # NOTE: 複数の値をテストする { 25, 30, 35 }

# 相対湿度[%]
rh_inner_C = 47.1
rh_outer_C = 40.5


class Test_COP推計_室内温度固定_外気温25:
    """ 論文掲載グラフと同一条件で整合するか確認
        室内温度を固定し、冷房負荷を変化させて COP の変化を見る
    """
    @classmethod
    def setup_class(cls):

        t_outer_C = 25
        cls._cdtn_C = Condition(
            T_ein = t_inner_C,
            T_cin = t_outer_C,
            X_ein = absolute_humid(rh_inner_C, t_inner_C),
            X_cin = absolute_humid(rh_outer_C, t_outer_C),
        )
        cls._M_ein = m3ph_to_kgDAps(v_inner * 60, cls._cdtn_C.T_ein)
        cls._M_cin = m3ph_to_kgDAps(v_outer * 60, cls._cdtn_C.T_cin)

    # NOTE: バリデーション値は論文掲載のグラフから読み取り
    def test_調査点1(self):
        q = 0.5; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 12.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点2(self):
        q = 1.0; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 14.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点3(self):
        q = 1.6; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 12.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点4(self):
        q = 2.0; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 10.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点5(self):
        q = 2.5; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP,  8.0, abs_tol=0.5), "論文掲載値と不整合"


class Test_COP推計_室内温度固定_外気温30:
    """ 論文掲載グラフと同一条件で整合するか確認
        室内温度を固定し、冷房負荷を変化させて COP の変化を見る
    """
    @classmethod
    def setup_class(cls):

        t_outer_C = 30
        cls._cdtn_C = Condition(
            T_ein = t_inner_C,
            T_cin = t_outer_C,
            X_ein = absolute_humid(rh_inner_C, t_inner_C),
            X_cin = absolute_humid(rh_outer_C, t_outer_C),
        )
        _logger.info(f"X_ein: {cls._cdtn_C.X_ein}")
        _logger.info(f"X_cin: {cls._cdtn_C.X_cin}")

        cls._M_ein = m3ph_to_kgDAps(v_inner * 60, cls._cdtn_C.T_ein)
        cls._M_cin = m3ph_to_kgDAps(v_outer * 60, cls._cdtn_C.T_cin)
        _logger.info(f"M_ein: {cls._M_ein}")
        _logger.info(f"M_cin: {cls._M_cin}")

    def test_調査点1(self):
        q = 0.5; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP,  8.0, abs_tol=0.7), "論文掲載値と不整合"  # FIXME: 精度?
    def test_調査点2(self):
        q = 1.0; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 10.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点3(self):
        q = 1.8; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP,  8.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点4(self):
        q = 2.7; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP,  6.0, abs_tol=0.5), "論文掲載値と不整合"

class Test_COP推計_室内温度固定_外気温35:
    """ 論文掲載グラフと同一条件で整合するか確認
        室内温度を固定し、冷房負荷を変化させて COP の変化を見る
    """
    @classmethod
    def setup_class(cls):

        t_outer_C = 35
        cls._cdtn_C = Condition(
            T_ein = t_inner_C,
            T_cin = t_outer_C,
            X_ein = absolute_humid(rh_inner_C, t_inner_C),
            X_cin = absolute_humid(rh_outer_C, t_outer_C),
        )
        cls._M_ein = m3ph_to_kgDAps(v_inner * 60, cls._cdtn_C.T_ein)
        cls._M_cin = m3ph_to_kgDAps(v_outer * 60, cls._cdtn_C.T_cin)

    def test_調査点1(self):
        q = 0.4; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 6.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点2(self):
        q = 1.4; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 7.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点3(self):
        q = 2.0; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 6.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点4(self):
        q = 2.7; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 5.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点5(self):
        q = 3.3; COP = simu_COP_C(q, Pc_ronbun_C, R_ronbun_C(q), self._M_ein, self._M_cin, self._cdtn_C)
        assert math.isclose(COP, 4.0, abs_tol=0.5), "論文掲載値と不整合"


def cdtn_factory_C(t_ein, t_cin) -> Condition:
    """ 論文内で検証している使用条件をベースに一部変数化したもの
    """
    return Condition(
        T_ein = t_ein,
        T_cin = t_cin,
        X_ein = absolute_humid(rh_inner_C, t_ein),  # 論文より
        X_cin = absolute_humid(rh_outer_C, t_cin),  # 論文より
    )

class Test_COP推計_冷房能力固定_外気温25:
    """ 論文掲載グラフと同一条件で整合するか確認
        冷房負荷を固定し、室内温度を変化させて COP の変化を見る
    """
    q = 2.2; R = R_ronbun_C(q)  # 論文より固定(kW)
    t_outer_C = 25  # 外気温 {25, 30, 35}
    M_cin = m3ph_to_kgDAps(v_outer * 60, t_outer_C)

    def test_調査点1(self):
        t_inner_C = 19
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP,  6.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点2(self):
        t_inner_C = 25
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP,  8.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点3(self):
        t_inner_C = 29
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP, 10.0, abs_tol=0.5), "論文掲載値と不整合"

class Test_COP推計_冷房能力固定_外気温30:
    """ 論文掲載グラフと同一条件で整合するか確認
        冷房負荷を固定し、室内温度を変化させて COP の変化を見る
    """
    q = 2.2; R = R_ronbun_C(q)  # 論文より固定(kW)
    t_outer_C = 30  # 外気温 {25, 30, 35}
    M_cin = m3ph_to_kgDAps(v_outer * 60, t_outer_C)

    def test_調査点1(self):
        t_inner_C = 19
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP, 5.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点2(self):
        t_inner_C = 24
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP, 6.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点3(self):
        t_inner_C = 27
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP, 7.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点4(self):
        t_inner_C = 30
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP, 8.0, abs_tol=0.5), "論文掲載値と不整合"

class Test_COP推計_冷房能力固定_外気温35:
    """ 論文掲載グラフと同一条件で整合するか確認
        冷房負荷を固定し、室内温度を変化させて COP の変化を見る
    """
    q = 2.2; R = R_ronbun_C(q)  # 論文より固定(kW)
    t_outer_C = 35  # 外気温 {25, 30, 35}
    M_cin = m3ph_to_kgDAps(v_outer * 60, t_outer_C)

    def test_調査点1(self):
        t_inner_C = 17
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP, 4.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点2(self):
        t_inner_C = 24
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP, 5.0, abs_tol=0.5), "論文掲載値と不整合"
    def test_調査点3(self):
        t_inner_C = 29
        cdtn = cdtn_factory_C(t_inner_C, self.t_outer_C)
        M_ein = m3ph_to_kgDAps(v_inner * 60, t_inner_C)
        COP = simu_COP_C(self.q, Pc_ronbun_C, self.R, M_ein, self.M_cin, cdtn)
        assert math.isclose(COP, 6.0, abs_tol=0.5), "論文掲載値と不整合"
