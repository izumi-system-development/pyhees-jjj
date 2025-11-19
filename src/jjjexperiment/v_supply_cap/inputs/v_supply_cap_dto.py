from dataclasses import dataclass
# NOTE: データクラスからどうしてもロジックを参照するときは遅延インポートする
from jjjexperiment.inputs.options import Vサプライの上限キャップ

@dataclass
class VSupplyCapDto:
    """F23-02 Vサプライの上限キャップ変更に関する設定値"""

    v_supply_cap_logic: Vサプライの上限キャップ = Vサプライの上限キャップ.従来
    """Vサプライの上限キャップ変更ロジック"""

    @classmethod
    def from_dict(cls, data: dict) -> 'VSupplyCapDto':
        kwargs = {}

        if 'change_V_supply_d_t_i_max' in data:
            v_supply_cap_logic = Vサプライの上限キャップ(int(data['change_V_supply_d_t_i_max']))
            kwargs['v_supply_cap_logic'] = v_supply_cap_logic

        return cls(**kwargs)
