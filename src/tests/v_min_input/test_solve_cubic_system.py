# NOTE: 村松様より提供いただいた「風量３乗近似式検討」PDFに則ったテスト
company_a = [
    ((910, 46), (1830, 215), (3.14*1e-8, 22.31)),
    ((910, 46), (2020, 277), (3.08*1e-8, 22.76)),
]
company_b = [
    ((240, 33), (1440, 290), (8.65*1e-8, 31.80)),
    ((240, 33), (1140, 200), (1.14*1e-7, 31.43)),
]
company_c = [
    ((200, 18), ( 900, 135), (1.62*1e-7, 16.70)),
    ((200, 18), (1260, 265), (1.24*1e-7, 17.01)),
]
company_d = [
    ((210, 10), ( 930,  95), (1.07*1e-7,  9.01)),
    ((210, 10), (1200, 190), (1.05*1e-7,  9.03)),
    ((550, 15), (1740, 210), (3.82*1e-8,  8.64)),
    ((550, 15), (1980, 310), (3.88*1e-8,  8.54)),
    ((560, 20), (2280, 400), (3.25*1e-8, 14.28)),
    ((600, 15), (1740, 180), (3.27*1e-8,  7.95)),
    ((600, 15), (1980, 250), (3.11*1e-8,  8.27)),
    ((650, 20), (2280, 320), (2.59*1e-8, 12.88)),
]
company_e = [
    # NOTE: ファン2台の合計風量
    ((340, 42), (1600, 380), (8.33*1e-8, 38.73)),
]
company_f = [
    ((910, 46), (1610, 154), (3.16*1e-8, 22.20)),
]

import pytest
from jjjexperiment.ac_min_volume_input.section4_2_a import _solve_cubic_system

class Test三乗方程式解法:
    """_solve_cubic_system関数のテスト"""

    @pytest.mark.parametrize("point1, point2, expect", company_a)
    def test_company_a_データ(self, point1, point2, expect):
        """Company A 全データのテスト"""
        # Arrange & Act
        x1, y1 = point1
        x2, y2 = point2
        a, b = _solve_cubic_system(x1, x2, y1, y2)
        exp_a, exp_b = expect
        # Assert
        assert a == pytest.approx(exp_a, rel=1e-2)
        assert b == pytest.approx(exp_b, rel=1e-2)

    @pytest.mark.parametrize("point1, point2, expect", company_b)
    def test_company_b_データ(self, point1, point2, expect):
        """Company B 全データのテスト"""
        # Arrange & Act
        x1, y1 = point1
        x2, y2 = point2
        a, b = _solve_cubic_system(x1, x2, y1, y2)
        exp_a, exp_b = expect
        # Assert
        assert a == pytest.approx(exp_a, rel=1e-2)
        assert b == pytest.approx(exp_b, rel=1e-2)

    @pytest.mark.parametrize("point1, point2, expect", company_c)
    def test_company_c_データ(self, point1, point2, expect):
        """Company C 全データのテスト"""
        # Arrange & Act
        x1, y1 = point1
        x2, y2 = point2
        a, b = _solve_cubic_system(x1, x2, y1, y2)
        exp_a, exp_b = expect
        # Assert
        assert a == pytest.approx(exp_a, rel=1e-2)
        assert b == pytest.approx(exp_b, rel=1e-2)

    @pytest.mark.parametrize("point1, point2, expect", company_d)
    def test_company_d_データ(self, point1, point2, expect):
        """Company D 全データのテスト"""
        # Arrange & Act
        x1, y1 = point1
        x2, y2 = point2
        a, b = _solve_cubic_system(x1, x2, y1, y2)
        exp_a, exp_b = expect
        # Assert
        assert a == pytest.approx(exp_a, rel=1e-2)
        assert b == pytest.approx(exp_b, rel=1e-2)

    @pytest.mark.parametrize("point1, point2, expect", company_e)
    def test_company_e_データ(self, point1, point2, expect):
        """Company E 全データのテスト"""
        # Arrange & Act
        x1, y1 = point1
        x2, y2 = point2
        a, b = _solve_cubic_system(x1, x2, y1, y2)
        exp_a, exp_b = expect
        # Assert
        assert a == pytest.approx(exp_a, rel=1e-2)
        assert b == pytest.approx(exp_b, rel=1e-2)

    @pytest.mark.parametrize("point1, point2, expect", company_f)
    def test_company_f_データ(self, point1, point2, expect):
        """Company F 全データのテスト"""
        # Arrange & Act
        x1, y1 = point1
        x2, y2 = point2
        a, b = _solve_cubic_system(x1, x2, y1, y2)
        exp_a, exp_b = expect
        # Assert
        assert a == pytest.approx(exp_a, rel=1e-2)
        assert b == pytest.approx(exp_b, rel=1e-2)
