import pytest
import json
import copy
import warnings

from jjjexperiment.main import calc
from jjjexperiment.logger import LimitedLoggerAdapter as _logger
from jjjexperiment.inputs.options import *

from test_utils.utils import *

class Test統合テスト_デフォルト入力時:

    with open(INPUT_SAMPLE_TYPE1_PATH, 'r') as f:
        _inputs1: dict = json.load(f)
    with open(INPUT_SAMPLE_TYPE2_PATH, 'r') as f:
        _inputs2: dict = json.load(f)
    with open(INPUT_SAMPLE_TYPE3_PATH, 'r') as f:
        _inputs3: dict = json.load(f)
    with open(INPUT_SAMPLE_TYPE4_PATH, 'r') as f:
        _inputs4: dict = json.load(f)

    def test_インプットデータ_前提確認(self, expected_inputs):
        """ テストコードが想定しているインプットデータかどうか確認
        """
        result = calc(self._inputs2, test_mode=True)

        assert result['TInput'].q_rtd_C == expected_inputs.q_rtd_C
        assert result['TInput'].q_rtd_H == expected_inputs.q_rtd_H
        assert result['TInput'].q_max_C == expected_inputs.q_max_C
        assert result['TInput'].q_max_H == expected_inputs.q_max_H
        assert result['TInput'].e_rtd_C == expected_inputs.e_rtd_C
        assert result['TInput'].e_rtd_H == expected_inputs.e_rtd_H

    def test_関数_deep_update(self):
        """ 階層のあるインプットを使用してインプットを拡張するテスト
        """
        fixtures = {
                "U_A": 0.60,  # 0.86
                "H_A": {"VAV": 2},
                "C_A": {"VAV": 2},
            }
        # 複製しないと別テストで矛盾する
        inputs_double = copy.deepcopy(self._inputs1)
        inputs = deep_update(inputs_double, fixtures)

        assert inputs["U_A"] == 0.60
        assert inputs["H_A"]["VAV"] == 2
        assert inputs["C_A"]["VAV"] == 2

    def test_計算結果一致_方式1(self, expected_result_type1):
        """ ipynbのサンプル入力で計算結果が意図しない変化がないことを確認
        """
        # warnings.simplefilter('error')

        inputs = copy.deepcopy(self._inputs1)
        # inputs = change_testmode_input_V_hs_min_H(inputs)
        # inputs = change_testmode_input_V_hs_min_C(inputs)
        # inputs = change_testmode_carryover(inputs)
        # inputs = change_testmode_VAV(inputs)
        # inputs = change_testmode_underfloor_old(inputs)
        # inputs = change_testmode_underfloor_new(inputs)
        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == pytest.approx(expected_result_type1.E_H, rel=1e-6)
        assert result['TValue'].E_C == pytest.approx(expected_result_type1.E_C, rel=1e-6)

    def test_計算結果一致_方式2(self, expected_result_type2):
        """ ipynbのサンプル入力で計算結果が意図しない変化がないことを確認
        """

        inputs = copy.deepcopy(self._inputs2)
        # inputs = change_testmode_input_V_hs_min_H(inputs)
        # inputs = change_testmode_input_V_hs_min_C(inputs)
        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C == expected_result_type2.E_C

    def test_計算結果一致_方式3(self, expected_result_type1, expected_result_type2):
        """ 方式3 最後まで実行できること、結果がちゃんと変わることだけ確認
        """

        inputs = copy.deepcopy(self._inputs3)
        # NOTE: 方式3では、最低風量の入力は無視されることが確認できます
        # inputs = change_testmode_input_V_hs_min_H(inputs)
        # inputs = change_testmode_input_V_hs_min_C(inputs)
        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C

    def test_計算結果一致_方式4(self, expected_result_type1, expected_result_type2):
        """ 方式4 最後まで実行できること、結果がちゃんと変わることだけ確認
        """
        inputs = copy.deepcopy(self._inputs4)
        # NOTE: 方式4では、最低風量の入力は無視されることが確認できます
        # inputs = change_testmode_input_V_hs_min_H(inputs)
        # inputs = change_testmode_input_V_hs_min_C(inputs)
        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C

def change_testmode_VAV(inputs: dict):
    fixtures = {
        "change_supply_volume_before_vav_adjust": VAVありなしの吹出風量.数式を統一する.value,
        "change_V_supply_d_t_i_max": Vサプライの上限キャップ.従来.value,
        "H_A": {"VAV": 2},
        "C_A": {"VAV": 2},
    }
    # 複製しないと別テストで矛盾する
    inputs_copied = copy.deepcopy(inputs)
    return deep_update(inputs_copied, fixtures)

def change_testmode_VAV_cap1logic(inputs: dict):
    """ VAVを負荷比で按分したときの上限キャップを有効
    """
    fixtures = {
        "change_supply_volume_before_vav_adjust": VAVありなしの吹出風量.数式を統一する.value,
        "change_V_supply_d_t_i_max": Vサプライの上限キャップ.設計風量_全室で均一.value,
        "H_A": {"VAV": 2},
        "C_A": {"VAV": 2},
    }
    inputs_copied = copy.deepcopy(inputs)  # 複製しないと別テストで矛盾する
    return deep_update(inputs_copied, fixtures)

def change_testmode_VAV_cap2logic(inputs: dict):
    """ VAVを負荷比で按分したときの上限キャップを有効
    """
    fixtures = {
        "change_supply_volume_before_vav_adjust": VAVありなしの吹出風量.数式を統一する.value,
        "change_V_supply_d_t_i_max": Vサプライの上限キャップ.設計風量_風量増室のみ.value,
        "H_A": {"VAV": 2},
        "C_A": {"VAV": 2},
    }
    inputs_copied = copy.deepcopy(inputs)  # 複製しないと別テストで矛盾する
    return deep_update(inputs_copied, fixtures)

def change_testmode_carryover(inputs: dict) -> dict:
    """ 熱繰越 """
    fixtures = {"carry_over_heat": 過剰熱量繰越計算.行う.value}
    inputs_copied = copy.deepcopy(inputs)  # 複製しないと別テストで矛盾する
    return deep_update(inputs_copied, fixtures)

def change_testmode_VAV(inputs: dict) -> dict:
    """ VAV """
    fixtures = {
        "H_A": {"VAV": 2},
        "C_A": {"VAV": 2},
    }
    inputs_copied = copy.deepcopy(inputs)
    return deep_update(inputs_copied, fixtures)

def change_testmode_input_V_hs_min_H(inputs: dict):
    """ 最低風量直接入力 - H """
    fixtures = {
        "H_A": {
            "input_V_hs_min_H": 最低風量直接入力.入力する.value,
            "V_hs_min_H": 1200,
        }
    }
    inputs_copied = copy.deepcopy(inputs)  # 複製しないと別テストで矛盾する
    return deep_update(inputs_copied, fixtures)

def change_testmode_input_V_hs_min_C(inputs: dict):
    """ 最低風量直接入力 - C """
    fixtures = {
        "C_A": {
            "input_V_hs_min_C": 最低風量直接入力.入力する.value,
            "V_hs_min_C": 1200,
        }
    }
    inputs_copied = copy.deepcopy(inputs)  # 複製しないと別テストで矛盾する
    return deep_update(inputs_copied, fixtures)

def change_testmode_underfloor_old(inputs: dict):
    """ 床下空調の古いロジック
    """
    fixtures = {"underfloor_air_conditioning_air_supply": 2}
    inputs_copied = copy.deepcopy(inputs)  # 複製しないと別テストで矛盾する
    return deep_update(inputs_copied, fixtures)

def change_testmode_underfloor_new(inputs: dict):
    """ 床下空調の新しいロジック
    """
    fixtures = {
        "change_underfloor_temperature": 床下空調ロジック.変更する.value,
        "input_ufac_consts": 2,  # 変える
        "Theta_g_avg": 15.7,
        "U_s_vert": 2.223,  # 既存式の値が過少なので入力
        "phi": 0.846,
    }
    inputs_copied = copy.deepcopy(inputs)  # 複製しないと別テストで矛盾する
    return deep_update(inputs_copied, fixtures)

def change_testmode_exploded_Q_UT(inputs: dict):
    """ 240115全館暖冷房委員会資料13-6における実行条件
        未処理負荷(一次エネルギー相当分)が大きいことが指摘されています
    """
    fixtures = {
        "H_A": {
            "input": 2,
            "q_hs_rtd": 5000,
            "P_hs_rtd": 900,
            "V_fan_rtd": 1377,
            "P_fan_rtd": 204,
        },
        "C_A": {
            "input": 2,
            "q_hs_rtd": 4000,
            "P_hs_rtd": 800,
            "V_fan_rtd": 1377,
            "P_fan_rtd": 204.3,
        },
    }
    # 複製しないと別テストで矛盾する
    inputs_copied = copy.deepcopy(inputs)
    return deep_update(inputs_copied, fixtures)
