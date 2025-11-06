import pytest
import json
import copy

from jjjexperiment.main import calc
from jjjexperiment.inputs.options import *

from test_utils.utils import *

class TestV最低風量入力結合:
    """V最低風量入力 (v_min_input) の結合テスト"""

    def _change_V_min_input(self, inputs: dict) -> dict:
        """最低風量直接入力を有効"""
        fixtures = {
            "H_A": {
                "input_V_hs_min_H": 最低風量直接入力.入力する.value,
                "V_hs_min_H": 1200,
            },
            "C_A": {
                "input_V_hs_min_C": 最低風量直接入力.入力する.value,
                "V_hs_min_C": 1200,
            }
        }
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)

    def _change_general_ventilation(self, inputs: dict, enabled: bool) -> dict:
        """全般換気設定"""
        fixtures = {
            "H_A": {"general_ventilation_H": enabled},
            "C_A": {"general_ventilation_C": enabled}
        }
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)

    def _change_E_min_input(self, inputs: dict, solve: ファン消費電力算定方法) -> dict:
        """最低電力直接入力を有効"""
        val = solve.value
        fixtures = {
            "H_A": {
                "input_E_E_fan_min_H": 最低電力直接入力.入力する.value,
                "E_E_fan_min_H": 100,
                "E_E_fan_logic_H": val
            },
            "C_A": {
                "input_E_E_fan_min_C": 最低電力直接入力.入力する.value,
                "E_E_fan_min_C": 100,
                "E_E_fan_logic_C": val
            }
        }
        inputs_copied = copy.deepcopy(inputs)
        return deep_update(inputs_copied, fixtures)

    _inputs1: dict = json.load(open(INPUT_SAMPLE_TYPE1_PATH, 'r'))
    _inputs2: dict = json.load(open(INPUT_SAMPLE_TYPE2_PATH, 'r'))
    _inputs3: dict = json.load(open(INPUT_SAMPLE_TYPE3_PATH, 'r'))
    _inputs4: dict = json.load(open(INPUT_SAMPLE_TYPE4_PATH, 'r'))

    # 最低風量直接入力 & タイプ3
    def test_Type3(self):
        """Type3で最低風量直接入力の動作確認"""
        # Arrange
        inputs = self._inputs3.copy()
        inputs = self._change_V_min_input(inputs)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        # Type3では潜熱評価モデルのため影響なし
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    # 最低風量直接入力 & タイプ1 x 最低電力入力あり・なし x 全般換気あり・なし
    def test_Type1_全般換気あり_最低電力なし(self):
        """Type1で最低電力なし・全般換気あり"""
        # Arrange
        inputs = self._inputs1.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, True)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    def test_Type1_全般換気なし_最低電力なし(self):
        """Type1で最低電力なし・全般換気なし"""
        # Arrange
        inputs = self._inputs1.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, False)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    def test_Type1_全般換気あり_最低電力あり_一次(self):
        """Type1で最低電力あり・全般換気あり"""
        # Arrange
        inputs = self._inputs1.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, True)
        inputs = self._change_E_min_input(inputs, ファン消費電力算定方法.直線近似法)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    def test_Type1_全般換気あり_最低電力あり_三次(self):
        """Type1で最低電力あり・全般換気あり"""
        # Arrange
        inputs = self._inputs1.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, True)
        inputs = self._change_E_min_input(inputs, ファン消費電力算定方法.風量三乗近似法)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    # 最低風量直接入力 & タイプ2 x 最低電力入力あり・なし x 全般換気あり・なし
    def test_Type2_全般換気なし_最低電力なし(self):
        """Type2で全般換気なし・最低電力なし"""
        # Arrange
        inputs = self._inputs2.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, False)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    def test_Type2_全般換気あり_最低電力なし(self):
        """Type2で全般換気あり・最低電力なし"""
        # Arrange
        inputs = self._inputs2.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, True)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    def test_Type2_全般換気あり_最低電力あり_一次(self):
        """Type2で最低電力あり・全般換気あり"""
        # Arrange
        inputs = self._inputs2.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, True)
        inputs = self._change_E_min_input(inputs, ファン消費電力算定方法.直線近似法)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    def test_Type2_全般換気あり_最低電力あり_三次(self):
        """Type2で最低電力あり・全般換気あり"""
        # Arrange
        inputs = self._inputs2.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, True)
        inputs = self._change_E_min_input(inputs, ファン消費電力算定方法.風量三乗近似法)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    # 最低風量直接入力 & タイプ4 x 最低電力入力あり・なし x 全般換気あり・なし
    def test_Type4_全般換気なし_最低電力なし(self):
        """Type4で全般換気なし・最低電力なし"""
        # Arrange
        inputs = self._inputs4.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, False)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    def test_Type4_全般換気あり_最低電力なし(self):
        """Type4で全般換気あり・最低電力なし"""
        # Arrange
        inputs = self._inputs4.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, True)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    def test_Type4_全般換気あり_最低電力あり_一次(self):
        """Type4で最低電力あり・全般換気あり"""
        # Arrange
        inputs = self._inputs4.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, True)
        inputs = self._change_E_min_input(inputs, ファン消費電力算定方法.直線近似法)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)

    def test_Type4_全般換気あり_最低電力あり_三次(self):
        """Type4で最低電力あり・全般換気あり"""
        # Arrange
        inputs = self._inputs4.copy()
        inputs = self._change_V_min_input(inputs)
        inputs = self._change_general_ventilation(inputs, True)
        inputs = self._change_E_min_input(inputs, ファン消費電力算定方法.風量三乗近似法)
        # Act
        result = calc(inputs, test_mode=True)
        # Assert
        t_value = result['TValue']
        assert isinstance(t_value.E_H, float)
        assert isinstance(t_value.E_C, float)
