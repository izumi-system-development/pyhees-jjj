import pytest
import json
import copy

from jjjexperiment.main import calc
from test_utils.utils import INPUT_SAMPLE_TYPE3_PATH, deep_update
from jjjexperiment.inputs.options import *


class Test潜熱評価統合テスト:
    """潜熱評価 (latent_load) の統合テスト - Type3ワークフローの検証"""

    _inputs_type3: dict = json.load(open(INPUT_SAMPLE_TYPE3_PATH, 'r'))

    def _change_testmode_VAV(self, inputs: dict) -> dict:
        """VAV設定変更"""
        fixtures = {
            "H_A": {"VAV": 2},
            "C_A": {"VAV": 2},
        }
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)

    def _change_testmode_input_V_hs_min_H(self, inputs: dict) -> dict:
        """最低風量直接入力 - 暖房"""
        fixtures = {
            "H_A": {
                "input_V_hs_min_H": 最低風量直接入力.入力する.value,
                "V_hs_min_H": 1200,
            }
        }
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)

    def _change_testmode_input_V_hs_min_C(self, inputs: dict) -> dict:
        """最低風量直接入力 - 冷房"""
        fixtures = {
            "C_A": {
                "input_V_hs_min_C": 最低風量直接入力.入力する.value,
                "V_hs_min_C": 1200,
            }
        }
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)

    def _change_testmode_fan_coeff_H(self, inputs: dict) -> dict:
        """暖房機の風量設定変更"""
        fixtures = {"H_A": {"fan_coeff": [0, 0, 27, -8, 13]}}
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)

    def _change_testmode_fan_coeff_C(self, inputs: dict) -> dict:
        """冷房機の風量設定変更"""
        fixtures = {"C_A": {"fan_coeff": [0, 0, 13, 20, -6]}}
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)

    def _change_testmode_compressor_coeff_H(self, inputs: dict) -> dict:
        """暖房機の圧縮比設定変更"""
        fixtures = {"H_A": {"compressor_coeff": [0, 0.153, -0.53, 0.53, 0]}}
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)

    def _change_testmode_compressor_coeff_C(self, inputs: dict) -> dict:
        """冷房機の圧縮比設定変更"""
        fixtures = {"C_A": {"compressor_coeff": [0, 0, -0.444, 0.444, 0]}}
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)


    def test_type3_basic_calculation(self):
        """Type3基本計算の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_input = result['TInput']
        t_value = result['TValue']
        assert t_value.E_H == pytest.approx(42533.87, abs=1e-1)
        assert t_value.E_C == pytest.approx(14641.53, abs=1e-1)

    def test_type3_energy_calculation(self):
        """Type3エネルギー計算の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        inputs = self._change_testmode_VAV(inputs)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_input = result['TInput']
        t_value = result['TValue']
        assert t_value.E_H == pytest.approx(42924.37, abs=1e-1)
        assert t_value.E_C == pytest.approx(14751.50, abs=1e-1)

    def test_type3_with_vav_variation1(self):
        """Type3 VAV設定変更の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        # タイプ3への影響はないこと
        inputs = self._change_testmode_input_V_hs_min_C(inputs)
        inputs = self._change_testmode_input_V_hs_min_H(inputs)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_input = result['TInput']
        t_value = result['TValue']
        assert t_value.E_H == pytest.approx(42533.87, abs=1e-1)
        assert t_value.E_C == pytest.approx(14641.53, abs=1e-1)

    def test_type3_with_vav_variation(self):
        """Type3 VAV設定変更の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        inputs = self._change_testmode_fan_coeff_C(inputs)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_input = result['TInput']
        t_value = result['TValue']
        assert t_value.E_H == pytest.approx(42533.87, abs=1e-1)
        assert t_value.E_C == pytest.approx(13730.61, abs=1e-1)

    def test_type3_with_min_airflow_variation(self):
        """Type3最低風量直接入力の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        inputs = self._change_testmode_fan_coeff_H(inputs)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_input = result['TInput']
        t_value = result['TValue']
        assert t_value.E_H == pytest.approx(42385.77, abs=1e-1)
        assert t_value.E_C == pytest.approx(14641.53, abs=1e-1)

    def test_type3_input_validation(self):
        """Type3入力値検証の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        inputs = self._change_testmode_compressor_coeff_C(inputs)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_input = result['TInput']
        t_value = result['TValue']
        assert t_value.E_H == pytest.approx(42533.87, abs=1e-1)
        assert t_value.E_C == pytest.approx(12127.15, abs=1e-1)

    def test_type3_efficiency_validation(self):
        """Type3効率値検証の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        inputs = self._change_testmode_compressor_coeff_H(inputs)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_input = result['TInput']
        t_value = result['TValue']
        assert t_value.E_H == pytest.approx(71069.76, abs=1e-1)
        assert t_value.E_C == pytest.approx(14641.53, abs=1e-1)
