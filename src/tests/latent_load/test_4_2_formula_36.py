import numpy as np
import json
import math

import pyhees.section4_2 as dc

# JJJ
import jjjexperiment.input as input
import jjjexperiment.constants as jjj_consts
# JJJ-Test
from test_utils.utils import INPUT_SAMPLE_TYPE3_PATH

class Test風量特性_熱源機:

    _H: np.ndarray
    _C: np.ndarray
    _M: np.ndarray
    _region: int

    _airvolume_minimum_H = 15.0  # m3/min
    _airvolume_minimum_C = 16.0  # m3/min
    _airvolume_maximum_H = 25.0  # m3/min
    _airvolume_maximum_C = 26.0  # m3/min

    _C1, _C0 = 2.4855, 10.209
    _H1, _H0 = 1.2946, 12.084

    @classmethod
    def setup_class(cls):
        """ 特性曲線を指定 """
        inputs = json.load(open(INPUT_SAMPLE_TYPE3_PATH, 'r'))
        fixture_C = {
            'airvolume_coeff': [0, 0, 0, cls._C1, cls._C0],
            'airvolume_minimum': cls._airvolume_minimum_C,
            'airvolume_maximum': cls._airvolume_maximum_C,
        }
        inputs['C_A'].update(fixture_C)
        fixture_H = {
            'airvolume_coeff': [0, 0, 0, cls._H1, cls._H0],
            'airvolume_minimum': cls._airvolume_minimum_H,
            'airvolume_maximum': cls._airvolume_maximum_H,
        }
        inputs['H_A'].update(fixture_H)
        jjj_consts.set_constants(inputs)

        _, _, _, _, _, cls._region, _ = input.get_basic(inputs)
        cls._H, cls._C, cls._M = dc.get_season_array_d_t(cls._region)

    def test_夏季の冷房出力_特性曲線上(self):
        def x(y):
            """簡易的に二次曲線でテストする"""
            return (y - jjj_consts.airvolume_coeff_a0_C) / jjj_consts.airvolume_coeff_a1_C

        x1 = x(jjj_consts.airvolume_minimum_C)
        x2 = x(jjj_consts.airvolume_maximum_C)
        x_mid = math.floor(x1 + (x2-x1) / 2)  # 非キャップ座標

        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(x_mid)
        sut = dc.get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=True)

        def y(x):
            """簡易的に二次曲線でテストする"""
            return jjj_consts.airvolume_coeff_a1_C * x + jjj_consts.airvolume_coeff_a0_C

        indices_C = np.where(self._C == True)[0]
        np.testing.assert_allclose(sut[indices_C], y(x_mid) * 60)  # m3/h

    def test_夏季の暖房出力_下限キャップ(self):
        # テキトーな高めの値 10.0 kw
        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(10)
        sut = dc.get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=False)

        # 夏季の暖房出力は最低値となる
        indices_C = np.where(self._C == True)[0]
        np.testing.assert_allclose(sut[indices_C], self._airvolume_minimum_H * 60)  # m3/h

    def test_夏季の冷房出力_上限キャップ(self):
        # ありえない高めの値 100.0 kw
        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(100)
        sut = dc.get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=True)

        # 夏季の冷房出力に上限キャップが有効
        indices_C = np.where(self._C == True)[0]
        np.testing.assert_allclose(sut[indices_C], self._airvolume_maximum_C * 60)  # m3/h

    def test_冬季の暖房出力_特性曲線上(self):
        def x(y):
            """簡易的に二次曲線でテストする"""
            return (y - jjj_consts.airvolume_coeff_a0_H) / jjj_consts.airvolume_coeff_a1_H

        x1 = x(jjj_consts.airvolume_minimum_H)
        x2 = x(jjj_consts.airvolume_maximum_H)
        x_mid = math.floor(x1 + (x2-x1) / 2)  # 非キャップ座標

        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(x_mid)
        sut = dc.get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=False)

        def y(x):
            """簡易的に二次曲線でテストする"""
            return jjj_consts.airvolume_coeff_a1_H * x + jjj_consts.airvolume_coeff_a0_H

        indices_H = np.where(self._H == True)[0]
        np.testing.assert_allclose(sut[indices_H], y(x_mid) * 60)  # m3/h

    def test_冬季の冷房出力_下限キャップ(self):
        # テキトーな高めの値 10.0 kw
        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(10)
        sut = dc.get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=True)

        # 冬季の冷房出力は最低値となる
        indices_H = np.where(self._H == True)[0]
        np.testing.assert_allclose(sut[indices_H], self._airvolume_minimum_C * 60)  # m3/h

    def test_冬季の暖房出力_上限キャップ(self):
        # ありえない高めの値 100.0 kw
        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(100)
        sut = dc.get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=False)

        # 冬季の暖房出力に上限キャップが有効
        indices_H = np.where(self._H == True)[0]
        np.testing.assert_allclose(sut[indices_H], self._airvolume_maximum_H * 60)  # m3/h

def kw2mjph(x: float) -> float:
    """ kW -> MJ/h へ単位変換する """
    return x * 3600 / 1000
