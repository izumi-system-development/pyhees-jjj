from dataclasses import dataclass
from typing import Optional
# JJJ
from jjjexperiment.options import *

@dataclass
class InputMinVolumeInput:
    input_V_hs_min: 最低風量直接入力 = 最低風量直接入力.入力しない
    """熱源機ファン最低風量の直接入力フラグ"""
    V_hs_min: Optional[float] = None
    """熱源機ファン最低風量の直接入力値 [m3/h]"""
    input_E_E_fan_min: 最低電力直接入力 = 最低電力直接入力.入力しない
    """熱源機ファン最低電力の直接入力フラグ"""
    E_E_fan_min: Optional[float] = 0.0
    """熱源機ファン最低電力の直接入力値 [W]"""
    E_E_fan_logic: ファン消費電力算定方法 = ファン消費電力算定方法.直線近似法
    """最低電力入力時 ファン消費電力算定方法"""

    @classmethod
    def from_dict(cls, data: dict) -> 'InputMinVolumeInput':
        """JSON辞書からインスタンスを作成"""
        kwargs = {}
        if 'input_V_hs_min' in data:
            kwargs['input_V_hs_min'] = 最低風量直接入力(int(data['input_V_hs_min']))

            if kwargs['input_V_hs_min'] == 最低風量直接入力.入力する.value:
                # 事前条件: 有効な入力値が存在する
                if 'V_hs_min' not in data:
                    raise Exception('V_hs_min 最低風量の直接入力がありません.')
                kwargs['V_hs_min'].V_hs_min = float(data['V_hs_min'])

                # NOTE: 最低電力直接入力は最低風量直接入力が有効なことが前提の仕様です
                if 'input_E_E_fan_min' in data:
                    kwargs['input_E_E_fan_min'] = 最低電力直接入力(int(data['input_E_E_fan_min']))

                    if kwargs['input_E_E_fan_min'] == 最低電力直接入力.入力する.value:
                        # 事前条件: 有効な入力値が存在する
                        if 'E_E_fan_min' not in data:
                            raise Exception('E_E_fan_min 最低電力の直接入力がありません.')
                        kwargs['E_E_fan_min'] = float(data['E_E_fan_min'])
                        # 事前条件: 電力算定方法の指定あり
                        if 'E_E_fan_logic' not in data:
                            raise Exception('E_E_fan_logic ファン消費電力算定方法の指定がありません.')
                        kwargs['E_E_fan_logic'] = ファン消費電力算定方法(int(data['E_E_fan_logic']))
        return cls(**kwargs)
