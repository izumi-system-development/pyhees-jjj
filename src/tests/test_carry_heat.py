import pytest
import math

from pyhees.section4_2 import *

class Test_計算式_面積バランス:
    """ 乾燥空気の密度[kg/m3]の計算が正しい
    """

    A_A = 120.80
    """面積全体"""
    A_MR = 29.81
    """メインルーム"""
    A_OR = 51.34
    """副ルーム"""

    """ A_HCZ_i: 暖冷房区画iの床面積 """
    def test_居室部分の床面積A_HCZ_iの合計(self):
        A_HCZ_i = np.array(
            [ld.get_A_HCZ_i(i, self.A_A, self.A_MR, self.A_OR) for i in range(1, 6)])
        A_HCZ = self.A_MR + self.A_OR  # 居室部分の床面積
        assert sum(A_HCZ_i) == pytest.approx(A_HCZ)

    def test_居室の数(self):
        A_HCZ_i = np.array(
            [ld.get_A_HCZ_i(i, self.A_A, self.A_MR, self.A_OR) for i in range(1, 6)])
        assert len(A_HCZ_i) == 5

    def test_風量バランスの合計(self):
        A_HCZ_i = np.array(
            [ld.get_A_HCZ_i(i, self.A_A, self.A_MR, self.A_OR) for i in range(1, 6)])
        r_supply_des_i = get_r_supply_des_i(A_HCZ_i)
        assert sum(r_supply_des_i) == 1
