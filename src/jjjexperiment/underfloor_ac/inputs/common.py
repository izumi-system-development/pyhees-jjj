import pandas as pd
from dataclasses import dataclass
# JJJ
from jjjexperiment.inputs.options import *

__all__ = ['UnderfloorAc', 'UfVarsDataFrame']

@dataclass
class UnderfloorAc:
    """F24-05 床下空調に関する設定値"""

    new_ufac_flg: 床下空調ロジック = 床下空調ロジック.変更しない

    # NOTE: 従来 pyhees では上書き対象でない定数たち
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

            if new_ufac_flg == 床下空調ロジック.変更する:
                # 実行条件: 明示的な上書き宣言が必要
                if 'input_ufac_consts' in data and int(data['input_ufac_consts']) == 2:
                    kwargs['Theta_g_avg'] = float(data['Theta_g_avg'])
                    kwargs['U_s_vert'] = float(data['U_s_vert'])
                    kwargs['phi'] = float(data['phi'])
        return cls(**kwargs)

class UfVarsDataFrame:
    '''床下空調 新ロジックの調査用 出力変数'''
    def __init__(self):
        # d_t 長のデータフレーム
        self._df_d_t = pd.DataFrame()

    def update_df(self, data: dict):
        # 横連結時は ignore_index しないこと
        self._df_d_t = pd.concat([self._df_d_t, pd.DataFrame(data)], axis=1)

    def export_to_csv(self, filename: str, encoding: str = 'cp932'):
        '''csv書き出し'''
        self._df_d_t.to_csv(filename, index=False, encoding=encoding)
