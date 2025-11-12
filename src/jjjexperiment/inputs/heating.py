# SeasonalLoadクラスは削除 - 新アーキテクチャではAcSetting + Entityパターンを使用
# HeatingAcSetting + HeatQuantityを使用してください
import pyhees.section4_3_a as rac_spec
from dataclasses import dataclass

@dataclass
class CRACSpecification:
    """暖房CRAC仕様"""

    q_rtd: float = 0.0
    """定格暖房能力 [W]"""
    q_max: float = 0.0
    """最大暖房能力 [W]"""
    e_rtd: float = 0.0
    """定格暖房エネルギー効率 [-]"""
    dualcompressor: bool = False
    """小能力時高効率型コンプレッサー"""
    input_C_af: dict = None
    """室内機吹き出し風量に関する出力補正係数の入力"""

    @classmethod
    def from_dict(cls, data: dict, q_rtd_C: float, q_max_C: float, e_rtd_C: float) -> 'CRACSpecification':
        # 機器性能
        if data.get('type') == 2 and int(data.get('input_rac_performance', 1)) == 2:
            q_rtd = float(data['q_rac_rtd_H'])
            q_max = float(data['q_rac_max_H'])
            e_rtd = float(data['e_rac_rtd_H'])
        elif data.get('type') == 4:
            q_rtd = float(data['q_rac_pub_rtd']) * 1000
            q_max = float(data['q_rac_pub_max']) * 1000
            e_rtd = rac_spec.get_e_rtd_H(e_rtd_C)
        else:
            q_rtd = rac_spec.get_q_rtd_H(q_rtd_C)
            q_max = rac_spec.get_q_max_H(q_rtd, q_max_C)
            e_rtd = rac_spec.get_e_rtd_H(e_rtd_C)

        dualcompressor = data.get('type') == 2 and int(data.get('dualcompressor', 1)) == 2

        input_C_af = {'input_mode': 2, 'dedicated_chamber': False, 'fixed_fin_direction': False, 'C_af_H': 1.0}
        # 方式ごとに入力項目があるため、typeを見て取得する値を変えます。
        # NOTE: 方式1はルームエアコンではないため入力がないはず
        if data.get('type') in [2, 3, 4]:
            suffix = str(data['type'])

            input_C_af['input_mode'] = int(data.get(f'input_C_af_H{suffix}', 2))
            if input_C_af['input_mode'] == 2:
                input_C_af['C_af_H'] = float(data.get(f'C_af_H{suffix}', 1.0))

            input_C_af['dedicated_chamber'] = int(data.get(f'dedicated_chamber{suffix}', 1)) == 2
            input_C_af['fixed_fin_direction'] = int(data.get(f'fixed_fin_direction{suffix}', 1)) == 2

        return cls(
            q_rtd=q_rtd, q_max=q_max, e_rtd=e_rtd,
            dualcompressor=dualcompressor, input_C_af=input_C_af
        )