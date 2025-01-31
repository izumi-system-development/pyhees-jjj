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

    @pytest.fixture
    def arrange_A_HCZ_i(self):
        """A_HCZ_i: 暖冷房区画iの床面積 [m2]"""
        return np.array([ld.get_A_HCZ_i(i, self.A_A, self.A_MR, self.A_OR) for i in range(1, 6)])

    def test_居室部分の床面積A_HCZ_iの合計(self, arrange_A_HCZ_i):
        # Act
        A_HCZ = self.A_MR + self.A_OR  # 居室部分の床面積
        # Assert
        assert sum(arrange_A_HCZ_i) == pytest.approx(A_HCZ)

    def test_居室の数(self, arrange_A_HCZ_i):
        # Assert
        assert len(arrange_A_HCZ_i) == 5

    def test_風量バランスの合計(self, arrange_A_HCZ_i):
        # Act
        r_supply_des_i = get_r_supply_des_i(arrange_A_HCZ_i)
        # Assert
        assert sum(r_supply_des_i) == 1
