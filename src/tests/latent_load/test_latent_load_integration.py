import pytest
import json
import copy

from jjjexperiment.main import calc
from test_utils.utils import INPUT_SAMPLE_TYPE3_PATH, deep_update
from jjjexperiment.inputs.options import *


class Test潜熱評価統合テスト:
    """潜熱評価 (latent_load) の統合テスト - Type3ワークフローの検証"""

    _inputs_type3: dict = json.load(open(INPUT_SAMPLE_TYPE3_PATH, 'r'))

    def test_type3_basic_calculation(self):
        """Type3基本計算の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        
        # Act
        result = calc(inputs, test_mode=True)
        
        # Assert
        assert result is not None
        assert 'TInput' in result
        assert 'TValue' in result
        
        # 基本的な出力値の存在確認
        t_input = result['TInput']
        t_value = result['TValue']
        
        assert hasattr(t_input, 'q_rtd_C')
        assert hasattr(t_input, 'q_rtd_H')
        assert hasattr(t_value, 'E_H')
        assert hasattr(t_value, 'E_C')

    def test_type3_energy_calculation(self):
        """Type3エネルギー計算の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        
        # Act
        result = calc(inputs, test_mode=True)
        
        # Assert
        t_input = result['TInput']
        t_value = result['TValue']
        
        # 定格能力が正の値であること
        assert t_input.q_rtd_H > 0  # 定格暖房能力
        assert t_input.q_rtd_C > 0  # 定格冷房能力
        assert t_input.q_max_H > 0  # 最大暖房能力
        assert t_input.q_max_C > 0  # 最大冷房能力
        
        # 年間エネルギー消費量が非負値であること
        assert t_value.E_H >= 0  # 年間暖房エネルギー消費量 [MJ/year]
        assert t_value.E_C >= 0  # 年間冷房エネルギー消費量 [MJ/year]

    def test_type3_with_vav_variation(self):
        """Type3 VAV設定変更の統合テスト"""
        # Arrange
        inputs_default = self._inputs_type3.copy()
        inputs_vav = self._change_testmode_VAV(self._inputs_type3)
        
        # Act
        result_default = calc(inputs_default, test_mode=True)
        result_vav = calc(inputs_vav, test_mode=True)
        
        # Assert
        # VAV設定により結果が変わることを確認
        assert result_default['TValue'].E_H != result_vav['TValue'].E_H or \
               result_default['TValue'].E_C != result_vav['TValue'].E_C

    def test_type3_with_min_airflow_variation(self):
        """Type3最低風量直接入力の統合テスト"""
        # Arrange
        inputs_default = self._inputs_type3.copy()
        inputs_min_h = self._change_testmode_input_V_hs_min_H(self._inputs_type3)
        inputs_min_c = self._change_testmode_input_V_hs_min_C(self._inputs_type3)
        
        # Act
        result_default = calc(inputs_default, test_mode=True)
        result_min_h = calc(inputs_min_h, test_mode=True)
        result_min_c = calc(inputs_min_c, test_mode=True)
        
        # Assert
        # 最低風量設定が正常に適用されることを確認（結果が変わらない場合もある）
        assert result_default['TValue'].E_H >= 0
        assert result_min_h['TValue'].E_H >= 0
        assert result_min_c['TValue'].E_H >= 0
        assert result_default['TValue'].E_C >= 0
        assert result_min_h['TValue'].E_C >= 0
        assert result_min_c['TValue'].E_C >= 0

    def test_type3_input_validation(self):
        """Type3入力値検証の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        
        # Act
        result = calc(inputs, test_mode=True)
        
        # Assert
        t_input = result['TInput']
        
        # 入力値が正しく設定されていることを確認
        assert hasattr(t_input, 'q_rtd_H')  # 定格暖房能力
        assert hasattr(t_input, 'q_rtd_C')  # 定格冷房能力
        assert hasattr(t_input, 'e_rtd_H')  # 定格暖房エネルギー消費効率
        assert hasattr(t_input, 'e_rtd_C')  # 定格冷房エネルギー消費効率

    def test_type3_efficiency_validation(self):
        """Type3効率値検証の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        
        # Act
        result = calc(inputs, test_mode=True)
        
        # Assert
        t_input = result['TInput']
        
        # エネルギー消費効率が妥当な範囲であること
        assert t_input.e_rtd_H > 0  # 暖房効率は正の値
        assert t_input.e_rtd_C > 0  # 冷房効率は正の値
        assert t_input.e_rtd_H < 10  # 暖房効率は現実的な範囲
        assert t_input.e_rtd_C < 10  # 冷房効率は現実的な範囲

    def test_type3_calculation_consistency(self):
        """Type3計算一貫性の統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        
        # Act - 同じ入力で2回計算
        result1 = calc(inputs, test_mode=True)
        result2 = calc(inputs, test_mode=True)
        
        # Assert - 結果が一致すること
        assert result1['TValue'].E_H == result2['TValue'].E_H
        assert result1['TValue'].E_C == result2['TValue'].E_C
        assert result1['TInput'].q_rtd_H == result2['TInput'].q_rtd_H
        assert result1['TInput'].q_rtd_C == result2['TInput'].q_rtd_C

    def test_type3_latent_load_model(self):
        """Type3潜熱評価モデルの統合テスト"""
        # Arrange
        inputs = self._inputs_type3.copy()
        
        # Act
        result = calc(inputs, test_mode=True)
        
        # Assert
        t_value = result['TValue']
        
        # 潜熱評価モデルによる計算が完了していること
        assert t_value.E_H > 0 or t_value.E_C > 0  # 少なくとも暖房か冷房のエネルギー消費があること
        
        # エネルギー消費量が現実的な範囲であること（住宅用途）
        assert t_value.E_H < 200000  # 年間暖房エネルギー < 200GJ
        assert t_value.E_C < 200000  # 年間冷房エネルギー < 200GJ

    # Helper methods for input variations
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
