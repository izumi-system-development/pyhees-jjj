import copy
import json
import pytest

from test_utils.utils import INPUT_SAMPLE_TYPE1_PATH, deep_update, expected_result_type1

from jjjexperiment.main import calc
from jjjexperiment.inputs.options import Vサプライの上限キャップ
from jjjexperiment.logger import LimitedLoggerAdapter as _logger

def change_testmode_V_supply_max(inputs: dict, logic: Vサプライの上限キャップ) -> dict:
    """Vサプライ上限キャップ設定変更"""
    fixtures = {"change_V_supply_d_t_i_max": logic.value}
    inputs_copied = copy.deepcopy(inputs)
    return deep_update(inputs_copied, fixtures)

class TestVサプライ上限キャップ結合:

    with open(INPUT_SAMPLE_TYPE1_PATH, 'r') as f:
        _inputs1: dict = json.load(f)

    def test_方式1_従来(self, expected_result_type1):
        inputs = copy.deepcopy(self._inputs1)
        inputs = change_testmode_V_supply_max(inputs, Vサプライの上限キャップ.従来)
        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == pytest.approx(expected_result_type1.E_H, rel=1e-6)
        assert result['TValue'].E_C == pytest.approx(expected_result_type1.E_C, rel=1e-6)

    def test_方式1_設計風量_全室で均一(self, expected_result_type1):
        inputs = copy.deepcopy(self._inputs1)
        inputs = change_testmode_V_supply_max(inputs, Vサプライの上限キャップ.設計風量_全室で均一)
        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == pytest.approx(expected_result_type1.E_H, rel=1e-6)
        assert result['TValue'].E_C == pytest.approx(expected_result_type1.E_C, rel=1e-6)

    def test_方式1_設計風量_風量増室のみ(self, expected_result_type1):
        inputs = copy.deepcopy(self._inputs1)
        inputs = change_testmode_V_supply_max(inputs, Vサプライの上限キャップ.設計風量_風量増室のみ)
        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == pytest.approx(expected_result_type1.E_H, rel=1e-6)
        assert result['TValue'].E_C == pytest.approx(expected_result_type1.E_C, rel=1e-6)
