from dataclasses import dataclass
from typing import Optional
# JJJ
from jjjexperiment.inputs.options import *

@dataclass
class UnderfloorAc:
    """F24-05 床下空調に関する設定値"""

    new_ufac_flg: 床下空調ロジック = 床下空調ロジック.変更しない

    # NOTE: pyhees では上書き対象でない定数たち
    """床下空調ロジック"""
    Theta_g_avg: float = 15.7
    """地盤内の不易層の温度 [℃]"""
    U_s_vert: float = 2.223
    """床板(床チャンバー上面)の熱貫流率 [W/(m2・K)]"""
    phi: float = 0.846
    """基礎(床チャンバー側面)の線熱貫流率 [W/(m・K)]"""

    @classmethod
    def from_dict(cls, data: dict) -> 'UnderfloorAc':
        kwargs = {}
        if 'change_underfloor_temperature' in data:
            new_ufac_flg = 床下空調ロジック(int(data['change_underfloor_temperature']))
            kwargs['new_ufac_flg'] = new_ufac_flg

            if new_ufac_flg == 床下空調ロジック.変更する.value:
                # 実行条件: 明示的な上書き宣言が必要
                if 'input_ufac_consts' in data and int(data['input_ufac_consts']) == 2:
                    kwargs['Theta_g_avg'] = float(data['Theta_g_avg'])
                    kwargs['U_s_vert'] = float(data['U_s_vert'])
                    kwargs['phi'] = float(data['phi'])
        return cls(**kwargs)
