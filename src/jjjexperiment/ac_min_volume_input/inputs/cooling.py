from dataclasses import dataclass
# JJJ
from jjjexperiment.inputs.options import *

@dataclass
class InputMinVolumeInput:
    input_V_hs_min: 最低風量直接入力 = 最低風量直接入力.入力しない
    """熱源機ファン最低風量の直接入力フラグ"""
    V_hs_min: float = 0.0
    """熱源機ファン最低風量の直接入力値 [m3/h]"""
    input_E_E_fan_min: 最低電力直接入力 = 最低電力直接入力.入力しない
    """熱源機ファン最低電力の直接入力フラグ"""
    E_E_fan_min: float = 0.0
    """熱源機ファン最低電力の直接入力値 [W]"""
    E_E_fan_logic: ファン消費電力算定方法 = ファン消費電力算定方法.直線近似法
    """最低電力入力時 ファン消費電力算定方法"""

    @classmethod
    def from_dict(cls, data: dict) -> 'InputMinVolumeInput':
        """JSON辞書からインスタンスを作成"""
        kwargs = {}
        if 'input_V_hs_min' in data:
            kwargs['input_V_hs_min'] = 最低風量直接入力(int(data['input_V_hs_min']))
        if 'V_hs_min' in data:
            kwargs['V_hs_min'] = float(data['V_hs_min'])
        if 'input_E_E_fan_min' in data:
            kwargs['input_E_E_fan_min'] = 最低電力直接入力(int(data['input_E_E_fan_min']))
        if 'E_E_fan_min' in data:
            kwargs['E_E_fan_min'] = float(data['E_E_fan_min'])
        if 'E_E_fan_logic' in data:
            kwargs['E_E_fan_logic'] = ファン消費電力算定方法(int(data['E_E_fan_logic']))
        return cls(**kwargs)
