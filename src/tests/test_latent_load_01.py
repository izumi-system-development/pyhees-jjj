import json
import copy
import numpy as np
import numpy.testing as nptest
import math

from pyhees.section3_2 import calc_r_env

from pyhees.section4_1 \
    import calc_heating_load, calc_cooling_load
from pyhees.section4_2 \
    import get_V_dash_hs_supply_d_t_2023, get_season_array_d_t
from pyhees.section4_2_a \
    import get_A_f_hex, get_A_e_hex, get_alpha_c_hex_C, get_alpha_c_hex_H, get_E_E_fan_H_d_t, get_E_E_fan_C_d_t, get_q_hs_C_d_t, get_q_hs_H_d_t



import jjjexperiment.input as input
from jjjexperiment.logger import LimitedLoggerAdapter as _logger

import jjjexperiment.constants as constants
from jjjexperiment.constants import PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_3

from jjjexperiment.section4_2 import calc_Q_UT_A
from jjjexperiment.section4_2_a import calc_E_E_H_d_t, get_E_E_C_d_t

from test_utils.utils import INPUT_SAMPLE_TYPE3_PATH

class Testコイル特性:

    _expected_T1T2 = {
        'A_f_hex': 0.23559,  # 仕様書より
        'A_e_hex': 6.396,    # 仕様書より
    }

    _expected_T3 = {
        'A_f_hex_upper': 0.3,  # 仕様書より
        'A_f_hex_lower': 0.2,  # 仕様書より
        'A_f_hex_custom': 0.23456,  # ユーザーの独自入力を想定
        'A_e_hex_upper': 10.6,  # 仕様書より
        'A_e_hex_lower': 6.2,   # 仕様書より
        'A_e_hex_custom': 6.66666,  # ユーザーの独自入力を想定
    }

    def test_有効面積_方式1_定格低(self):
        """ 定格能力 5.6 kW 未満で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == get_A_f_hex(PROCESS_TYPE_1, 5500)
        assert self._expected_T1T2['A_e_hex'] == get_A_e_hex(PROCESS_TYPE_1, 5500)
    def test_有効面積_方式1_定格BVA(self):
        """ 定格能力 5.6 kW 丁度で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == get_A_f_hex(PROCESS_TYPE_1, 5600)
        assert self._expected_T1T2['A_e_hex'] == get_A_e_hex(PROCESS_TYPE_1, 5600)
    def test_有効面積_方式1_定格高(self):
        """ 定格能力 5.6 kW 以上で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == get_A_f_hex(PROCESS_TYPE_1, 5700)
        assert self._expected_T1T2['A_e_hex'] == get_A_e_hex(PROCESS_TYPE_1, 5700)

    def test_有効面積_方式2_定格低(self):
        """ 定格能力 5.6 kW 未満で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == get_A_f_hex(PROCESS_TYPE_2, 5500)
        assert self._expected_T1T2['A_e_hex'] == get_A_e_hex(PROCESS_TYPE_2, 5500)
    def test_有効面積_方式2_定格BVA(self):
        """ 定格能力 5.6 kW 丁度で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == get_A_f_hex(PROCESS_TYPE_2, 5600)
        assert self._expected_T1T2['A_e_hex'] == get_A_e_hex(PROCESS_TYPE_2, 5600)
    def test_有効面積_方式2_定格高(self):
        """ 定格能力 5.6 kW 以上で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == get_A_f_hex(PROCESS_TYPE_2, 5700)
        assert self._expected_T1T2['A_e_hex'] == get_A_e_hex(PROCESS_TYPE_2, 5700)

    def test_有効面積_方式3_定格低(self):
        """ 定格能力 5.6 kW 未満で 仕様書通り """
        assert self._expected_T3['A_f_hex_lower'] == get_A_f_hex(PROCESS_TYPE_3, 5500)
        assert self._expected_T3['A_e_hex_lower'] == get_A_e_hex(PROCESS_TYPE_3, 5500)
    def test_有効面積_方式3_定格BVA(self):
        """ 定格能力 5.6 kW 丁度で 仕様書通り """
        assert self._expected_T3['A_f_hex_upper'] == get_A_f_hex(PROCESS_TYPE_3, 5600)
        assert self._expected_T3['A_e_hex_upper'] == get_A_e_hex(PROCESS_TYPE_3, 5600)
    def test_有効面積_方式3_定格高(self):
        """ 定格能力 5.6 kW 以上で 仕様書通り """
        assert self._expected_T3['A_f_hex_upper'] == get_A_f_hex(PROCESS_TYPE_3, 5700)
        assert self._expected_T3['A_e_hex_upper'] == get_A_e_hex(PROCESS_TYPE_3, 5700)


class Testコイル特性_方式3_ユーザー独自値:
    """ 潜熱評価モデル時のコイル特性の係数はユーザーの独自値が設定可能としています
    """
    _custom_values = {
        'H_A': {
            'A_f_hex_small': 0.12345,  # ユーザーの独自入力を想定
            'A_e_hex_small': 6.66666,  # ユーザーの独自入力を想定
            'A_f_hex_large': 0.23456,  # ユーザーの独自入力を想定
            'A_e_hex_large': 7.77777,  # ユーザーの独自入力を想定
        }
    }
    _default_values = {
        'H_A': {
            'A_f_hex_small': 0.2,   # 規定値
            'A_e_hex_small': 6.2,   # 規定値
            'A_f_hex_large': 0.3,   # 規定値
            'A_e_hex_large': 10.6,  # 規定値
        }
    }
    @classmethod
    def setup_class(cls):
        """ ユーザーカスタム値を適用する """
        constants.set_constants(cls._custom_values)

    @classmethod
    def teardown_class(cls):
        """ ユーザーカスタム値をデフォルト値に戻す """
        constants.set_constants(cls._default_values)

    def test_有効面積_方式3_定格低_上書き(self):
        """ 定格能力 5.6 kW 未満で 仕様書通り """
        assert self._custom_values['H_A']['A_f_hex_small'] == get_A_f_hex(PROCESS_TYPE_3, 5500)
        assert self._custom_values['H_A']['A_e_hex_small'] == get_A_e_hex(PROCESS_TYPE_3, 5500)
    def test_有効面積_方式3_定格BVA_上書き(self):
        """ 定格能力 5.6 kW 丁度で 仕様書通り """
        assert self._custom_values['H_A']['A_f_hex_large'] == get_A_f_hex(PROCESS_TYPE_3, 5600)
        assert self._custom_values['H_A']['A_e_hex_large'] == get_A_e_hex(PROCESS_TYPE_3, 5600)
    def test_有効面積_方式3_定格高_上書き(self):
        """ 定格能力 5.6 kW 以上で 仕様書通り """
        assert self._custom_values['H_A']['A_f_hex_large'] == get_A_f_hex(PROCESS_TYPE_3, 5700)
        assert self._custom_values['H_A']['A_e_hex_large'] == get_A_e_hex(PROCESS_TYPE_3, 5700)

class Test熱伝達特性_冷房:

    @property
    def excel_values(self) -> dict:
        """ 参考Excelより 新kx 値のテスト
            V_hs_supply: 熱源機の風量 [m3/h]
            new_kx: 定格冷却能力 5.6kW 時の熱伝達率[W/m2・K] (0:未満, 1:以上)
        """
        return {
            'V_hs_supply': [
                None,
                0.248253754663786 * 3600,
                0.253488350731205 * 3600,
                0.394065672493681 * 3600,
            ],
            'new_kx': [
                None,
                (0.0798240595964243, 0.0537160397309496),
                (0.0814755746556952, 0.0548170497704635),
                (0.125827719671756, 0.0843851464478376),
            ],
            'type': PROCESS_TYPE_3,
            'X_hs_in': 8.0,  # ダミー値
        }

    def test_数式_方式3_エクセル値試験_01(self):
        args = {
            'type': self.excel_values['type'],
            'V_fan_x_C': self.excel_values['V_hs_supply'][1],
            'X_hs_in': self.excel_values['X_hs_in'],
        }
        _, a_dash_c_hex_C_small = get_alpha_c_hex_C(**args, q_hs_rtd_C = 5599)  # 5600未満
        _, a_dash_c_hex_C_large = get_alpha_c_hex_C(**args, q_hs_rtd_C = 5600)  # 5600以上
        assert math.isclose(a_dash_c_hex_C_small, self.excel_values['new_kx'][1][0])
        assert math.isclose(a_dash_c_hex_C_large, self.excel_values['new_kx'][1][1])

    def test_数式_方式3_エクセル値試験_02(self):
        args = {
            'type': self.excel_values['type'],
            'V_fan_x_C': self.excel_values['V_hs_supply'][2],
            'X_hs_in': self.excel_values['X_hs_in'],
        }
        _, a_dash_c_hex_C_small = get_alpha_c_hex_C(**args, q_hs_rtd_C = 5599)  # 5600未満
        _, a_dash_c_hex_C_large = get_alpha_c_hex_C(**args, q_hs_rtd_C = 5600)  # 5600以上
        assert math.isclose(a_dash_c_hex_C_small, self.excel_values['new_kx'][2][0])
        assert math.isclose(a_dash_c_hex_C_large, self.excel_values['new_kx'][2][1])

    def test_数式_方式3_エクセル値試験_03(self):
        args = {
            'type': self.excel_values['type'],
            'V_fan_x_C': self.excel_values['V_hs_supply'][3],
            'X_hs_in': self.excel_values['X_hs_in'],
        }
        _, a_dash_c_hex_C_small = get_alpha_c_hex_C(**args, q_hs_rtd_C = 5599)  # 5600未満
        _, a_dash_c_hex_C_large = get_alpha_c_hex_C(**args, q_hs_rtd_C = 5600)  # 5600以上
        assert math.isclose(a_dash_c_hex_C_small, self.excel_values['new_kx'][3][0])
        assert math.isclose(a_dash_c_hex_C_large, self.excel_values['new_kx'][3][1])

    def test_室内熱交換器表面_熱伝達率_方式3_変化(self):
        """ 方式3(潜熱評価モデル)時のみ 計算結果が変化する
        """
        fixture = {
            'V': 120,
            'X': 0.010376,  # 表5 より
            'q': 800,
        }
        a1, a1_dash = get_alpha_c_hex_C(
                            type = PROCESS_TYPE_1,
                            V_fan_x_C  = fixture['V'],
                            X_hs_in    = fixture['X'],
                            q_hs_rtd_C = fixture['q'])
        a2, a2_dash = get_alpha_c_hex_C(
                            type = PROCESS_TYPE_2,
                            V_fan_x_C  = fixture['V'],
                            X_hs_in    = fixture['X'],
                            q_hs_rtd_C = fixture['q'])
        a3, a3_dash = get_alpha_c_hex_C(
                            type = PROCESS_TYPE_3,
                            V_fan_x_C  = fixture['V'],
                            X_hs_in    = fixture['X'],
                            q_hs_rtd_C = fixture['q'])

        assert a1 == a2, "結果が変わるべきでない両者の結果に差があります"
        assert a3 != a1 and a3 != a2, "変更されるべき 顕熱伝達率計算が変化していません"
        assert a1_dash == a2_dash, "結果が変わるべきでない両者の結果に差があります"
        assert a3_dash != a1_dash and a3_dash != a2_dash, "変更されるべき 潜熱伝達率計算が変化していません"


class Test熱伝達特性_暖房:

    def test_室内熱交換器表面_熱伝達率_方式3_変化(self):
        """ 方式3(潜熱評価モデル)時のみ 計算結果が変化する
        """
        fixture = {
            'V': 120,
            'q': 800,
        }
        a1 = get_alpha_c_hex_H(
            type = PROCESS_TYPE_1,
            V_fan_x_H = fixture['V'],
            q_hs_rtd_C = fixture['q'])
        a2 = get_alpha_c_hex_H(
            type = PROCESS_TYPE_2,
            V_fan_x_H = fixture['V'],
            q_hs_rtd_C = fixture['q'])
        a3 = get_alpha_c_hex_H(
            type = PROCESS_TYPE_3,
            V_fan_x_H = fixture['V'],
            q_hs_rtd_C = fixture['q'])

        assert a1 == a2, "結果が変わるべきでない両者の結果に差があります"
        assert a3 != a1 and a3 != a2, "変更されるべき 熱伝達率計算が変化していません"

def kw2mjph(x: float) -> float:
    """ kW -> MJ/h へ単位変換する """
    return x * 3600 / 1000


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
        constants.set_constants(inputs)

        _, _, _, _, _, cls._region, _ = input.get_basic(inputs)
        cls._H, cls._C, cls._M = get_season_array_d_t(cls._region)

    def test_夏季の冷房出力_特性曲線上(self):
        def x(y):
            """簡易的に二次曲線でテストする"""
            return (y - constants.airvolume_coeff_a0_C) / constants.airvolume_coeff_a1_C

        x1 = x(constants.airvolume_minimum_C)
        x2 = x(constants.airvolume_maximum_C)
        x_mid = math.floor(x1 + (x2-x1) / 2)  # 非キャップ座標

        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(x_mid)
        sut = get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=True)

        def y(x):
            """簡易的に二次曲線でテストする"""
            return constants.airvolume_coeff_a1_C * x + constants.airvolume_coeff_a0_C

        indices_C = np.where(self._C == True)[0]
        nptest.assert_allclose(sut[indices_C], y(x_mid) * 60)  # m3/h

    def test_夏季の暖房出力_下限キャップ(self):
        # テキトーな高めの値 10.0 kw
        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(10)
        sut = get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=False)

        # 夏季の暖房出力は最低値となる
        indices_C = np.where(self._C == True)[0]
        nptest.assert_allclose(sut[indices_C], self._airvolume_minimum_H * 60)  # m3/h

    def test_夏季の冷房出力_上限キャップ(self):
        # ありえない高めの値 100.0 kw
        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(100)
        sut = get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=True)

        # 夏季の冷房出力に上限キャップが有効
        indices_C = np.where(self._C == True)[0]
        nptest.assert_allclose(sut[indices_C], self._airvolume_maximum_C * 60)  # m3/h

    def test_冬季の暖房出力_特性曲線上(self):
        def x(y):
            """簡易的に二次曲線でテストする"""
            return (y - constants.airvolume_coeff_a0_H) / constants.airvolume_coeff_a1_H

        x1 = x(constants.airvolume_minimum_H)
        x2 = x(constants.airvolume_maximum_H)
        x_mid = math.floor(x1 + (x2-x1) / 2)  # 非キャップ座標

        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(x_mid)
        sut = get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=False)

        def y(x):
            """簡易的に二次曲線でテストする"""
            return constants.airvolume_coeff_a1_H * x + constants.airvolume_coeff_a0_H

        indices_H = np.where(self._H == True)[0]
        nptest.assert_allclose(sut[indices_H], y(x_mid) * 60)  # m3/h

    def test_冬季の冷房出力_下限キャップ(self):
        # テキトーな高めの値 10.0 kw
        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(10)
        sut = get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=True)

        # 冬季の冷房出力は最低値となる
        indices_H = np.where(self._H == True)[0]
        nptest.assert_allclose(sut[indices_H], self._airvolume_minimum_C * 60)  # m3/h

    def test_冬季の暖房出力_上限キャップ(self):
        # ありえない高めの値 100.0 kw
        Q_hat_hs_d_t = np.ones(24 * 365) * kw2mjph(100)
        sut = get_V_dash_hs_supply_d_t_2023(Q_hat_hs_d_t, self._region, for_cooling=False)

        # 冬季の暖房出力に上限キャップが有効
        indices_H = np.where(self._H == True)[0]
        nptest.assert_allclose(sut[indices_H], self._airvolume_maximum_H * 60)  # m3/h


def prepare_args_for_calc_Q_UT_A() -> dict:
    inputs = json.load(open(INPUT_SAMPLE_TYPE3_PATH, 'r'))

    inputs["H_A"]["input_V_hs_dsgn_H"] = 2  # ユーザー入力ON
    inputs["C_A"]["input_V_hs_dsgn_C"] = 2  # ユーザー入力ON
    constants.set_constants(inputs)

    # 個別の変数に展開
    _, _, A_A, A_MR, A_OR, region, sol_region = input.get_basic(inputs)
    ENV, NV_MR, NV_OR, TS, r_A_ufvnt, uflr_insul, uflr_air_cdtn_air_spl, hs_CAV = input.get_env(inputs)
    mode_H, H_A, _, _, _  = input.get_heating(inputs, region, A_A)
    mode_C, C_A, _, _     = input.get_cooling(inputs, region, A_A)
    q_rtd_C, q_rtd_H, q_max_C, q_max_H, e_rtd_C, e_rtd_H, dualcompressor_C, dualcompressor_H, input_C_af_C, input_C_af_H \
        = input.get_CRAC_spec(inputs)

    # 設計風量[m3/h]
    V_hs_dsgn_H, V_hs_dsgn_C = H_A['V_hs_dsgn_H'], C_A['V_hs_dsgn_C']  # NOTE: ユーザー入力ON時のみ可

    fixtures = {
        "case_name": "-",
        "climateFile": "-",
        "loadFile": "-",
        "Q": 2.647962191872085,
        "mu_C": 0.07170453031312457,
        "mu_H": 0.11011767155229846,
        "YUCACO_r_A_ufvnt": 0.7089130102430821,
        "HEX": None,
        "SHC": None,
        "R_g": None,
        "spec_MR": None,
        "spec_OR": None,
        "mode_MR": None,
        "mode_OR": None,
    }

    L_H_d_t_i: np.ndarray  # H: 暖房負荷 [MJ/h]
    L_H_d_t_i, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i = calc_heating_load(
        region = region,
        sol_region = sol_region,
        A_A = A_A, A_MR = A_MR, A_OR = A_OR,
        NV_MR = NV_MR, NV_OR = NV_OR, TS = TS,
        r_A_ufvnt = r_A_ufvnt,
        underfloor_insulation = uflr_insul,
        mode_H = mode_H, mode_C = mode_C,
        Q =    fixtures["Q"],
        mu_H = fixtures["mu_H"],
        mu_C = fixtures["mu_C"],
        spec_MR = fixtures["spec_MR"],
        spec_OR = fixtures["spec_OR"],
        mode_MR = fixtures["mode_MR"],
        mode_OR = fixtures["mode_OR"],
        HEX = fixtures["HEX"],
        SHC = fixtures["SHC"])

    L_CS_d_t_i: np.ndarray  # CS: 冷房・顕熱負荷 [MJ/h]
    L_CL_d_t_i: np.ndarray  # CL: 冷房・潜熱負荷 [MJ/h]
    L_CS_d_t_i, L_CL_d_t_i = calc_cooling_load(
        region = region,
        A_A = A_A, A_MR = A_MR, A_OR = A_OR,
        NV_MR = NV_MR, NV_OR = NV_OR, TS = TS,
        r_A_ufvnt = r_A_ufvnt,
        underfloor_insulation = uflr_insul,
        mode_C = mode_C, mode_H = mode_H,
        Q =    fixtures["Q"],
        mu_H = fixtures["mu_H"],
        mu_C = fixtures["mu_C"],
        mode_MR = fixtures["mode_MR"],
        mode_OR = fixtures["mode_OR"],
        HEX =     fixtures["HEX"])

    r_env = calc_r_env(
        method='当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法',
        A_env=ENV['A_env'],
        A_A=A_A
    )

    main_args = {
        'case_name': fixtures['case_name'],
        'A_A': A_A,
        'A_MR': A_MR,
        'A_OR': A_OR,
        'r_env': r_env,  # A_env から変更
        'mu_H': fixtures["mu_H"],
        'mu_C': fixtures["mu_C"],
        'q_rtd_H': q_rtd_H,
        'q_rtd_C': q_rtd_C,
        'q_max_H': q_max_H,
        'q_max_C': q_max_C,
        'Q': fixtures["Q"],
        'hs_CAV': hs_CAV,
        'region': region,
        'L_H_d_t_i': L_H_d_t_i,
        'L_CS_d_t_i': L_CS_d_t_i,
        'L_CL_d_t_i': L_CL_d_t_i,
        'input_C_af_H': input_C_af_H,
        'input_C_af_C': input_C_af_C,
        'underfloor_insulation': uflr_insul,
        'underfloor_air_conditioning_air_supply': uflr_air_cdtn_air_spl,
        'YUCACO_r_A_ufvnt': fixtures["YUCACO_r_A_ufvnt"],
        # 'R_g': fixtures["R_g"],
        'climateFile': fixtures["climateFile"],
        'L_dash_H_R_d_t_i': L_dash_H_R_d_t_i,
        'L_dash_CS_R_d_t_i': L_dash_CS_R_d_t_i,
        'r_A_ufvnt': r_A_ufvnt
    }
    H_args = {
        'VAV': H_A['VAV'],
        'general_ventilation': H_A['general_ventilation'],
        'duct_insulation': H_A['duct_insulation'],
        'type': H_A['type'],  # NOTE: type と混合注意
        'q_hs_rtd_H': H_A['q_hs_rtd_H'],
        "q_hs_rtd_C": C_A['q_hs_rtd_C'],  # NOTE: 後に None で上書きするが必要
        'V_hs_dsgn_H': V_hs_dsgn_H,
        'V_hs_dsgn_C': None,  # NOTE: 暖房時除外項目
    }
    C_args = {
        'VAV': C_A['VAV'],
        'general_ventilation': C_A['general_ventilation'],
        'duct_insulation': C_A['duct_insulation'],
        'type': C_A['type'],  # NOTE: type と混合注意
        'q_hs_rtd_H': H_A['q_hs_rtd_H'],  # NOTE: 後に None で上書きするが必要
        "q_hs_rtd_C": C_A['q_hs_rtd_C'],
        'V_hs_dsgn_H': None,  # NOTE: 冷房時除外項目
        'V_hs_dsgn_C': V_hs_dsgn_C,
    }
    others = {
        'q_hs_min_H':  H_A['q_hs_min_H'],
        'q_hs_min_C':  C_A['q_hs_min_C'],
        'q_hs_mid_H':  H_A['q_hs_mid_H'],
        "q_hs_mid_C":  C_A['q_hs_mid_C'],
        'P_hs_mid_H':  H_A['P_hs_mid_H'],
        "P_hs_mid_C":  C_A['P_hs_mid_C'],
        'V_fan_mid_H': H_A['V_fan_mid_H'],
        "V_fan_mid_C": C_A['V_fan_mid_C'],
        'P_fan_mid_H': H_A['P_fan_mid_H'],
        "P_fan_mid_C": C_A['P_fan_mid_C'],
        'V_fan_rtd_H': H_A['V_fan_rtd_H'],
        "V_fan_rtd_C": C_A['V_fan_rtd_C'],
        'e_rtd_H': e_rtd_H,
        "e_rtd_C": e_rtd_C,
        'P_fan_rtd_H': H_A['P_fan_rtd_H'],
        "P_fan_rtd_C": C_A['P_fan_rtd_C'],
        'P_hs_rtd_H': H_A['P_hs_rtd_H'],
        "P_hs_rtd_C": C_A['P_hs_rtd_C'],
        'dualcompressor_H': dualcompressor_H,
        "dualcompressor_C": dualcompressor_C,
        'EquipmentSpec_H': H_A['EquipmentSpec'],
        "EquipmentSpec_C": C_A['EquipmentSpec'],
        'f_SFP_H': H_A['f_SFP_H'],
        "f_SFP_C": C_A['f_SFP_C'],
    }
    return main_args, H_args, C_args, others


class Testファン消費電力_暖房:

    def prepareArgs(self) -> dict:
        """ 暖房用のセットアップ
        """
        main_args, H_args, _, others = prepare_args_for_calc_Q_UT_A()
        H_args['q_hs_rtd_C'] = None  # NOTE: 暖房負荷の計算時には冷房の定格出力は無視する
        main_args.update(H_args)

        _, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, _, _, _, V_hs_supply_d_t, V_hs_vent_d_t, C_df_H_d_t \
            = calc_Q_UT_A(**main_args)

        q_hs_H_d_t = get_q_hs_H_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, V_hs_supply_d_t, C_df_H_d_t, main_args['region'])

        return {
            'type': H_args['type'],
            'P_fan_rtd_H': others['P_fan_rtd_H'],
            'V_hs_vent_d_t': V_hs_vent_d_t,
            'V_hs_supply_d_t': V_hs_supply_d_t,
            'V_hs_dsgn_H': H_args['V_hs_dsgn_H'],
            'q_hs_H_d_t': q_hs_H_d_t,
            'f_SFP': others['f_SFP_H'],
        }

    _testBaseArgs: dict

    @classmethod
    def setup_class(cls):
        """ 暖房方式 以外の引数は共通として、方式ごとの挙動差のみを確認する
        """
        cls._testBaseArgs = cls.prepareArgs(cls)

    def test_方式1_方式2_結果一致(self):
        self._testBaseArgs['type'] = PROCESS_TYPE_1
        result_01 = get_E_E_fan_H_d_t(**self._testBaseArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_2
        result_02 = get_E_E_fan_H_d_t(**self._testBaseArgs)
        assert np.all(result_01 == result_02)

    def test_方式1_方式3_計算切替(self):
        self._testBaseArgs['type'] = PROCESS_TYPE_1
        result_01 = get_E_E_fan_H_d_t(**self._testBaseArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_3
        result_03 = get_E_E_fan_H_d_t(**self._testBaseArgs)
        assert not np.all(result_01 == result_03)

    def test_方式2_方式3_計算切替(self):
        self._testBaseArgs['type'] = PROCESS_TYPE_2
        result_02 = get_E_E_fan_H_d_t(**self._testBaseArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_3
        result_03 = get_E_E_fan_H_d_t(**self._testBaseArgs)
        assert not np.all(result_02 == result_03)

    def test_方式3_係数設定_変更反映(self):
        """ 同じ方式3でもユーザーが設定した係数によって計算結果が異なることを確認
        """
        self._testBaseArgs['type'] = PROCESS_TYPE_3
        update_info_01 = {
            'H_A': {'fan_coeff': [0, 0, 27, -8, 13]}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_01)
        result_03_01 = get_E_E_fan_H_d_t(**self._testBaseArgs)
        update_info_02 = {
            'H_A': {'fan_coeff': [0, 0, 13, 20, -6]}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_02)
        result_03_02 = get_E_E_fan_H_d_t(**self._testBaseArgs)

        assert not np.all(result_03_01 == result_03_02)


class Testファン消費電力_冷房:

    def prepareArgs(self) -> dict:
        """ 冷房用のセットアップ
        """
        main_args, _, C_args, others = prepare_args_for_calc_Q_UT_A()
        C_args['q_hs_rtd_H'] = None  # NOTE: 冷房負荷の計算時には暖房の定格出力は無視する
        main_args.update(C_args)

        _, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, _, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, V_hs_vent_d_t, _ \
            = calc_Q_UT_A(**main_args)

        q_hs_C_d_t = get_q_hs_C_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, main_args['region'])

        return {
            'type': C_args['type'],
            'P_fan_rtd_C': others['P_fan_rtd_C'],
            'V_hs_vent_d_t': V_hs_vent_d_t,
            'V_hs_supply_d_t': V_hs_supply_d_t,
            'V_hs_dsgn_C': C_args['V_hs_dsgn_C'],
            'q_hs_C_d_t': q_hs_C_d_t,
            'f_SFP': others['f_SFP_C'],
        }

    _testBaseArgs: dict

    @classmethod
    def setup_class(cls):
        """ 冷房方式 以外の引数は共通として、方式ごとの挙動差のみを確認する
        """
        cls._testBaseArgs = cls.prepareArgs(cls)

    def test_方式1_方式2_結果一致(self):
        self._testBaseArgs['type'] = PROCESS_TYPE_1
        result_01 = get_E_E_fan_C_d_t(**self._testBaseArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_2
        result_02 = get_E_E_fan_C_d_t(**self._testBaseArgs)
        assert np.all(result_01 == result_02)

    def test_方式1_方式3_計算切替(self):
        self._testBaseArgs['type'] = PROCESS_TYPE_1
        result_01 = get_E_E_fan_C_d_t(**self._testBaseArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_3
        result_03 = get_E_E_fan_C_d_t(**self._testBaseArgs)
        assert not np.all(result_01 == result_03)

    def test_方式2_方式3_計算切替(self):
        self._testBaseArgs['type'] = PROCESS_TYPE_2
        result_02 = get_E_E_fan_C_d_t(**self._testBaseArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_3
        result_03 = get_E_E_fan_C_d_t(**self._testBaseArgs)
        assert not np.all(result_02 == result_03)

    def test_方式3_係数設定_変更反映(self):
        """ 同じ方式3でもユーザーが設定した係数によって計算結果が異なることを確認
        """
        self._testBaseArgs['type'] = PROCESS_TYPE_3
        update_info_01 = {
            'C_A': {'fan_coeff': [0, 0, 27, -8, 13]}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_01)
        result_03_01 = get_E_E_fan_C_d_t(**self._testBaseArgs)
        update_info_02 = {
            'C_A': {'fan_coeff': [0, 0, 13, 20, -6]}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_02)
        result_03_02 = get_E_E_fan_C_d_t(**self._testBaseArgs)

        assert not np.all(result_03_01 == result_03_02)


class Testコンプレッサ効率特性_暖房:

    def prepareArgs(self) -> dict:
        """ 暖房用のセットアップ
        """
        main_args, H_args, _, others = prepare_args_for_calc_Q_UT_A()
        q_hs_rtd_C = H_args['q_hs_rtd_C']
        H_args['q_hs_rtd_C'] = None  # NOTE: 暖房負荷の計算時には冷房の定格出力は無視する
        main_args.update(H_args)

        _, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t, _, _, V_hs_supply_d_t, V_hs_vent_d_t, C_df_H_d_t \
            = calc_Q_UT_A(**main_args)

        # 送風機の消費電力[W] = 設計風量[m3/h] * 比消費電力[W/(m3/h)]
        P_rac_fan_rtd_H = H_args['V_hs_dsgn_H'] * others['f_SFP_H']

        return {
            "case_name": "Test",
            "Theta_hs_out_d_t": Theta_hs_out_d_t,
            "Theta_hs_in_d_t":  Theta_hs_in_d_t,
            "Theta_ex_d_t":     Theta_ex_d_t,
            "V_hs_supply_d_t":  V_hs_supply_d_t,
            "V_hs_vent_d_t":   V_hs_vent_d_t,
            "V_hs_dsgn_H":     H_args['V_hs_dsgn_H'],
            "C_df_H_d_t":      C_df_H_d_t,
            "P_rac_fan_rtd_H": P_rac_fan_rtd_H,
            "q_hs_min_H":  others['q_hs_min_H'],
            "q_hs_mid_H":  others['q_hs_mid_H'],
            "P_hs_mid_H":  others['P_hs_mid_H'],
            "V_fan_mid_H": others['V_fan_mid_H'],
            "P_fan_mid_H": others['P_fan_mid_H'],
            "q_max_C": main_args['q_max_C'],
            "q_max_H": main_args['q_max_H'],
            "q_rtd_C": main_args['q_rtd_C'],
            "q_hs_rtd_C": q_hs_rtd_C,  # NOTE: 暖房時であっても必要
            "q_rtd_H": main_args['q_rtd_H'],
            "e_rtd_H": others['e_rtd_H'],
            "V_fan_rtd_H": others['V_fan_rtd_H'],
            "P_fan_rtd_H": others['P_fan_rtd_H'],
            "q_hs_rtd_H":  H_args['q_hs_rtd_H'],
            "P_hs_rtd_H":  others['P_hs_rtd_H'],
            "type":   H_args['type'],
            "region": main_args['region'],
            "dualcompressor_H": others['dualcompressor_H'],
            "input_C_af_H":  main_args['input_C_af_H'],
            "EquipmentSpec": others['EquipmentSpec_H'],
            "f_SFP_H":       others['f_SFP_H'],
            "climateFile": main_args['climateFile'],
        }

    _testBaseArgs: dict

    @classmethod
    def setup_class(cls):
        """ 暖房方式 以外の引数は共通として、方式ごとの挙動差のみを確認する
        """
        cls._testBaseArgs = cls.prepareArgs(cls)

    def test_時間別消費電力量_方式1_方式3_送風機不変(self):

        self._testBaseArgs["type"] = PROCESS_TYPE_1
        _, _, E_E_fan_H_d_t1 = calc_E_E_H_d_t(**self._testBaseArgs)
        self._testBaseArgs["type"] = PROCESS_TYPE_3
        _, _, E_E_fan_H_d_t3 = calc_E_E_H_d_t(**self._testBaseArgs)

        # TODO: (5) ファン消費電力 の実装によって変更があるが仕様通りがチェック
        assert not np.array_equal(E_E_fan_H_d_t1, E_E_fan_H_d_t3), "送風機分の消費電力には方式による差が生じるはずです"

    def test_時間別消費電力量_方式1_方式3_合計値変化(self):

        self._testBaseArgs["type"] = PROCESS_TYPE_1
        E_E_H_d_t1, _, _ = calc_E_E_H_d_t(**self._testBaseArgs)
        self._testBaseArgs["type"] = PROCESS_TYPE_3
        E_E_H_d_t3, _, _ = calc_E_E_H_d_t(**self._testBaseArgs)

        assert not np.array_equal(E_E_H_d_t1, E_E_H_d_t3), "方式によって消費電力の計算値には差が生じなければなりません"

    def test_時間別消費電力量_方式1_方式2_両方変化(self):

        self._testBaseArgs["type"] = PROCESS_TYPE_1
        E_E_H_d_t1, _, E_E_fan_H_d_t1 = calc_E_E_H_d_t(**self._testBaseArgs)
        self._testBaseArgs["type"] = PROCESS_TYPE_2
        E_E_H_d_t2, _, E_E_fan_H_d_t2 = calc_E_E_H_d_t(**self._testBaseArgs)

        assert np.array_equal(E_E_fan_H_d_t1, E_E_fan_H_d_t2), "誤って送風機分の消費電力にも方式による差が生じています"
        assert not np.array_equal(E_E_H_d_t1, E_E_H_d_t2), "方式によって消費電力の計算値には差が生じなければなりません"

    def test_時間別消費電力量_方式3_係数設定有効(self):
        """ コンプレッサ効率特性曲線のパラメータ設定が結果に反映されていることを確認
        """
        self._testBaseArgs["type"] = PROCESS_TYPE_3
        # コンプレッサ効率特性 係数は Type3 でのみ有効
        coeffs_01 = [0, 0, -0.444, 0.444, 0]
        coeffs_02 = [0, 0.153, -0.53, 0.53, 0]

        update_info_01 = {
            'H_A': {'compressor_coeff': coeffs_01}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_01)
        E_E_H_d_t_T301, _, E_E_fan_H_d_t_T301 = calc_E_E_H_d_t(**self._testBaseArgs)

        update_info_02 = {
            'H_A': {'compressor_coeff': coeffs_02}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_02)
        E_E_H_d_t_T302, _, E_E_fan_H_d_t_T302 = calc_E_E_H_d_t(**self._testBaseArgs)

        assert not np.array_equal(E_E_H_d_t_T301, E_E_H_d_t_T302), "コンプレッサ効率特性曲線の係数が結果に反映されていません"
        assert np.array_equal(E_E_fan_H_d_t_T301, E_E_fan_H_d_t_T302), "誤って送風機分の消費電力にも方式による差が生じています"

class Testコンプレッサ効率特性_冷房:

    def prepareArgs(self) -> dict:
        """ 冷房用のセットアップ
        """
        main_args, _, C_args, others = prepare_args_for_calc_Q_UT_A()
        q_hs_rtd_H = C_args['q_hs_rtd_H']  # NOTE: 暖房と異なる点で使用しない
        C_args['q_hs_rtd_H'] = None  # NOTE: 冷房負荷の計算時には暖房の定格出力は無視する
        main_args.update(C_args)

        _, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, V_hs_vent_d_t, _ \
            = calc_Q_UT_A(**main_args)

        # 送風機の消費電力[W] = 設計風量[m3/h] * 比消費電力[W/(m3/h)]
        P_rac_fan_rtd_C = C_args['V_hs_dsgn_C'] * others['f_SFP_C']

        return {
            "case_name": "Test",
            "Theta_hs_out_d_t": Theta_hs_out_d_t,
            "Theta_hs_in_d_t":  Theta_hs_in_d_t,
            "Theta_ex_d_t": Theta_ex_d_t,
            "V_hs_supply_d_t": V_hs_supply_d_t,
            "V_hs_vent_d_t": V_hs_vent_d_t,
            "V_hs_dsgn_C": C_args['V_hs_dsgn_C'],
            "X_hs_out_d_t": X_hs_out_d_t,
            "X_hs_in_d_t": X_hs_in_d_t,
            "q_hs_min_C":  others['q_hs_min_C'],
            "q_hs_mid_C":  others['q_hs_mid_C'],
            "P_hs_mid_C":  others['P_hs_mid_C'],
            "V_fan_mid_C": others['V_fan_mid_C'],
            "P_fan_mid_C": others['P_fan_mid_C'],
            "q_max_C": main_args['q_max_C'],
            "q_hs_rtd_C":  C_args['q_hs_rtd_C'],  # NOTE: 冷房時であっても必要
            "P_hs_rtd_C":  others['P_hs_rtd_C'],
            "V_fan_rtd_C": others['V_fan_rtd_C'],
            "P_fan_rtd_C": others['P_fan_rtd_C'],
            "q_rtd_C": main_args['q_rtd_C'],
            "e_rtd_C": others['e_rtd_C'],
            "P_rac_fan_rtd_C": P_rac_fan_rtd_C,
            "type":   C_args['type'],
            "region": main_args['region'],
            "dualcompressor_C": others['dualcompressor_C'],
            "input_C_af_C":  main_args['input_C_af_C'],
            "EquipmentSpec": others['EquipmentSpec_C'],
            "f_SFP_C": others['f_SFP_C'],
            "climateFile": main_args['climateFile'],
        }

    _testBaseArgs: dict

    @classmethod
    def setup_class(cls):
        """ 冷房方式 以外の引数は共通として、方式ごとの挙動差のみを確認する
        """
        cls._testBaseArgs = cls.prepareArgs(cls)

    def test_時間別消費電力量_方式1_方式3_送風機不変(self):

        self._testBaseArgs["type"] = PROCESS_TYPE_1
        _, E_E_fan_C_d_t_T1, _, _ = get_E_E_C_d_t(**self._testBaseArgs)
        self._testBaseArgs["type"] = PROCESS_TYPE_3
        _, E_E_fan_C_d_t_T3, _, _ = get_E_E_C_d_t(**self._testBaseArgs)

        # TODO: (5) ファン消費電力 の実装によって変更があるが仕様通りがチェック
        assert not np.array_equal(E_E_fan_C_d_t_T1, E_E_fan_C_d_t_T3), "送風機分の消費電力には方式による差が生じるはずです"

    def test_時間別消費電力量_方式1_方式3_平均冷房能力不変(self):

        self._testBaseArgs["type"] = PROCESS_TYPE_1
        _, _, q_hs_CS_d_t_T1, q_hs_CL_d_t_T1 = get_E_E_C_d_t(**self._testBaseArgs)
        self._testBaseArgs["type"] = PROCESS_TYPE_3
        _, _, q_hs_CS_d_t_T3, q_hs_CL_d_t_T3 = get_E_E_C_d_t(**self._testBaseArgs)

        assert np.array_equal(q_hs_CS_d_t_T1, q_hs_CS_d_t_T3), "誤って平均冷房顕熱能力にも方式による差が生じています"
        assert np.array_equal(q_hs_CL_d_t_T1, q_hs_CL_d_t_T3), "誤って平均冷房潜熱能力にも方式による差が生じています"

    def test_時間別消費電力量_方式1_方式3_合計値変化(self):

        self._testBaseArgs["type"] = PROCESS_TYPE_1
        E_E_C_d_t_T1, _, _, _ = get_E_E_C_d_t(**self._testBaseArgs)
        self._testBaseArgs["type"] = PROCESS_TYPE_3
        E_E_C_d_t_T3, _, _, _ = get_E_E_C_d_t(**self._testBaseArgs)

        assert not np.array_equal(E_E_C_d_t_T1, E_E_C_d_t_T3), "方式によって消費電力の計算値には差が生じなければなりません"

    def test_時間別消費電力量_方式1_方式2_両方変化(self):

        self._testBaseArgs["type"] = PROCESS_TYPE_1
        E_E_C_d_t_T1, E_E_fan_C_d_t_T1, _, _ = get_E_E_C_d_t(**self._testBaseArgs)
        self._testBaseArgs["type"] = PROCESS_TYPE_2
        E_E_C_d_t_T2, E_E_fan_C_d_t_T2, _, _ = get_E_E_C_d_t(**self._testBaseArgs)

        assert np.array_equal(E_E_fan_C_d_t_T1, E_E_fan_C_d_t_T2), "誤って送風機分の消費電力にも方式による差が生じています"
        assert not np.array_equal(E_E_C_d_t_T1, E_E_C_d_t_T2), "方式によって消費電力の計算値には差が生じなければなりません"

    def test_時間別消費電力量_方式3_係数設定有効(self):
        """ コンプレッサ効率特性曲線のパラメータ設定が結果に反映されていることを確認
        """
        self._testBaseArgs["type"] = PROCESS_TYPE_3
        # コンプレッサ効率特性 係数は Type3 でのみ有効
        coeffs_01 = [0, 0, -0.444, 0.444, 0]
        coeffs_02 = [0, 0.153, -0.53, 0.53, 0]

        update_info_01 = {
            'C_A': {'compressor_coeff': coeffs_01}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_01)
        E_E_C_d_t_T301, E_E_fan_C_d_t_T301, _, _ = get_E_E_C_d_t(**self._testBaseArgs)

        update_info_02 = {
            'C_A': {'compressor_coeff': coeffs_02}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_02)
        E_E_C_d_t_T302, E_E_fan_C_d_t_T302, _, _ = get_E_E_C_d_t(**self._testBaseArgs)

        assert not np.array_equal(E_E_C_d_t_T301, E_E_C_d_t_T302), "コンプレッサ効率特性曲線の係数が結果に反映されていません"
        assert np.array_equal(E_E_fan_C_d_t_T301, E_E_fan_C_d_t_T302), "誤って送風機分の消費電力にも方式による差が生じています"

