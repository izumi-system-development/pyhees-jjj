import math
import pyhees.section4_2_a as dc_a

# JJJ
import jjjexperiment.constants as constants
from jjjexperiment.constants import PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_3

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
        assert self._expected_T1T2['A_f_hex'] == dc_a.get_A_f_hex(PROCESS_TYPE_1, 5500)
        assert self._expected_T1T2['A_e_hex'] == dc_a.get_A_e_hex(PROCESS_TYPE_1, 5500)
    def test_有効面積_方式1_定格BVA(self):
        """ 定格能力 5.6 kW 丁度で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == dc_a.get_A_f_hex(PROCESS_TYPE_1, 5600)
        assert self._expected_T1T2['A_e_hex'] == dc_a.get_A_e_hex(PROCESS_TYPE_1, 5600)
    def test_有効面積_方式1_定格高(self):
        """ 定格能力 5.6 kW 以上で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == dc_a.get_A_f_hex(PROCESS_TYPE_1, 5700)
        assert self._expected_T1T2['A_e_hex'] == dc_a.get_A_e_hex(PROCESS_TYPE_1, 5700)

    def test_有効面積_方式2_定格低(self):
        """ 定格能力 5.6 kW 未満で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == dc_a.get_A_f_hex(PROCESS_TYPE_2, 5500)
        assert self._expected_T1T2['A_e_hex'] == dc_a.get_A_e_hex(PROCESS_TYPE_2, 5500)
    def test_有効面積_方式2_定格BVA(self):
        """ 定格能力 5.6 kW 丁度で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == dc_a.get_A_f_hex(PROCESS_TYPE_2, 5600)
        assert self._expected_T1T2['A_e_hex'] == dc_a.get_A_e_hex(PROCESS_TYPE_2, 5600)
    def test_有効面積_方式2_定格高(self):
        """ 定格能力 5.6 kW 以上で 仕様書通り """
        assert self._expected_T1T2['A_f_hex'] == dc_a.get_A_f_hex(PROCESS_TYPE_2, 5700)
        assert self._expected_T1T2['A_e_hex'] == dc_a.get_A_e_hex(PROCESS_TYPE_2, 5700)

    def test_有効面積_方式3_定格低(self):
        """ 定格能力 5.6 kW 未満で 仕様書通り """
        assert self._expected_T3['A_f_hex_lower'] == dc_a.get_A_f_hex(PROCESS_TYPE_3, 5500)
        assert self._expected_T3['A_e_hex_lower'] == dc_a.get_A_e_hex(PROCESS_TYPE_3, 5500)
    def test_有効面積_方式3_定格BVA(self):
        """ 定格能力 5.6 kW 丁度で 仕様書通り """
        assert self._expected_T3['A_f_hex_upper'] == dc_a.get_A_f_hex(PROCESS_TYPE_3, 5600)
        assert self._expected_T3['A_e_hex_upper'] == dc_a.get_A_e_hex(PROCESS_TYPE_3, 5600)
    def test_有効面積_方式3_定格高(self):
        """ 定格能力 5.6 kW 以上で 仕様書通り """
        assert self._expected_T3['A_f_hex_upper'] == dc_a.get_A_f_hex(PROCESS_TYPE_3, 5700)
        assert self._expected_T3['A_e_hex_upper'] == dc_a.get_A_e_hex(PROCESS_TYPE_3, 5700)


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
        assert self._custom_values['H_A']['A_f_hex_small'] == dc_a.get_A_f_hex(PROCESS_TYPE_3, 5500)
        assert self._custom_values['H_A']['A_e_hex_small'] == dc_a.get_A_e_hex(PROCESS_TYPE_3, 5500)
    def test_有効面積_方式3_定格BVA_上書き(self):
        """ 定格能力 5.6 kW 丁度で 仕様書通り """
        assert self._custom_values['H_A']['A_f_hex_large'] == dc_a.get_A_f_hex(PROCESS_TYPE_3, 5600)
        assert self._custom_values['H_A']['A_e_hex_large'] == dc_a.get_A_e_hex(PROCESS_TYPE_3, 5600)
    def test_有効面積_方式3_定格高_上書き(self):
        """ 定格能力 5.6 kW 以上で 仕様書通り """
        assert self._custom_values['H_A']['A_f_hex_large'] == dc_a.get_A_f_hex(PROCESS_TYPE_3, 5700)
        assert self._custom_values['H_A']['A_e_hex_large'] == dc_a.get_A_e_hex(PROCESS_TYPE_3, 5700)


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
        _, a_dash_c_hex_C_small = dc_a.get_alpha_c_hex_C(**args, q_hs_rtd_C = 5599)  # 5600未満
        _, a_dash_c_hex_C_large = dc_a.get_alpha_c_hex_C(**args, q_hs_rtd_C = 5600)  # 5600以上
        assert math.isclose(a_dash_c_hex_C_small, self.excel_values['new_kx'][1][0])
        assert math.isclose(a_dash_c_hex_C_large, self.excel_values['new_kx'][1][1])

    def test_数式_方式3_エクセル値試験_02(self):
        args = {
            'type': self.excel_values['type'],
            'V_fan_x_C': self.excel_values['V_hs_supply'][2],
            'X_hs_in': self.excel_values['X_hs_in'],
        }
        _, a_dash_c_hex_C_small = dc_a.get_alpha_c_hex_C(**args, q_hs_rtd_C = 5599)  # 5600未満
        _, a_dash_c_hex_C_large = dc_a.get_alpha_c_hex_C(**args, q_hs_rtd_C = 5600)  # 5600以上
        assert math.isclose(a_dash_c_hex_C_small, self.excel_values['new_kx'][2][0])
        assert math.isclose(a_dash_c_hex_C_large, self.excel_values['new_kx'][2][1])

    def test_数式_方式3_エクセル値試験_03(self):
        args = {
            'type': self.excel_values['type'],
            'V_fan_x_C': self.excel_values['V_hs_supply'][3],
            'X_hs_in': self.excel_values['X_hs_in'],
        }
        _, a_dash_c_hex_C_small = dc_a.get_alpha_c_hex_C(**args, q_hs_rtd_C = 5599)  # 5600未満
        _, a_dash_c_hex_C_large = dc_a.get_alpha_c_hex_C(**args, q_hs_rtd_C = 5600)  # 5600以上
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
        a1, a1_dash = dc_a.get_alpha_c_hex_C(
                            type = PROCESS_TYPE_1,
                            V_fan_x_C  = fixture['V'],
                            X_hs_in    = fixture['X'],
                            q_hs_rtd_C = fixture['q'])
        a2, a2_dash = dc_a.get_alpha_c_hex_C(
                            type = PROCESS_TYPE_2,
                            V_fan_x_C  = fixture['V'],
                            X_hs_in    = fixture['X'],
                            q_hs_rtd_C = fixture['q'])
        a3, a3_dash = dc_a.get_alpha_c_hex_C(
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
        a1 = dc_a.get_alpha_c_hex_H(
            type = PROCESS_TYPE_1,
            V_fan_x_H = fixture['V'],
            q_hs_rtd_C = fixture['q'])
        a2 = dc_a.get_alpha_c_hex_H(
            type = PROCESS_TYPE_2,
            V_fan_x_H = fixture['V'],
            q_hs_rtd_C = fixture['q'])
        a3 = dc_a.get_alpha_c_hex_H(
            type = PROCESS_TYPE_3,
            V_fan_x_H = fixture['V'],
            q_hs_rtd_C = fixture['q'])

        assert a1 == a2, "結果が変わるべきでない両者の結果に差があります"
        assert a3 != a1 and a3 != a2, "変更されるべき 熱伝達率計算が変化していません"
