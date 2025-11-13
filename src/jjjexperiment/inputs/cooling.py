from dataclasses import dataclass

# NOTE: データクラスからどうしてもロジックを参照するときは遅延インポートする

@dataclass
class CRACSpecification:
    """冷房CRAC仕様"""

    q_rtd: float = 0.0
    """定格冷房能力 [W]"""
    q_max: float = 0.0
    """最大冷房能力 [W]"""
    e_rtd: float = 0.0
    """エネルギー消費効率 [-]"""
    dualcompressor: bool = False
    """小能力時高効率型コンプレッサー"""
    input_C_af: dict = None
    """室内機吹き出し風量に関する出力補正係数の入力"""

    @classmethod
    def from_dict(cls, data: dict, A_A: float) -> 'CRACSpecification':
        # エネルギー消費効率入力 冷房のみ
        e_class = None
        if int(data.get('input_mode', 1)) == 2:
            mode = int(data.get('mode', 1))
            e_class = {1: 'い', 2: 'ろ', 3: 'は'}.get(mode)

        # 機器性能
        from pyhees.section4_3_a import get_e_rtd_C, get_q_rtd_C, get_q_max_C
        if data.get('type') == 2 and int(data.get('input_rac_performance', 1)) == 2:
            q_rtd = float(data['q_rac_rtd_C'])
            q_max = float(data['q_rac_max_C'])
            e_rtd = float(data['e_rac_rtd_C'])
        elif data.get('type') == 4:
            q_rtd = float(data['q_rac_pub_rtd']) * 1000
            q_max = float(data['q_rac_pub_max']) * 1000
            e_rtd = get_e_rtd_C(e_class, q_rtd)
        else:
            q_rtd = get_q_rtd_C(A_A)
            q_max = get_q_max_C(q_rtd)
            e_rtd = get_e_rtd_C(e_class, q_rtd)

        dualcompressor = data.get('type') == 2 and int(data.get('dualcompressor', 1)) == 2

        input_C_af = {'input_mode': 2, 'dedicated_chamber': False, 'fixed_fin_direction': False, 'C_af_C': 1.0}
        # 方式ごとに入力項目があるため、typeを見て取得する値を変えます。
        # NOTE: 方式1はルームエアコンではないため入力がないはず
        if data.get('type') in [2, 3, 4]:
            suffix = str(data['type'])

            input_C_af['input_mode'] = int(data.get(f'input_C_af_C{suffix}', 2))
            if input_C_af['input_mode'] == 2:
                input_C_af['C_af_C'] = float(data.get(f'C_af_C{suffix}', 1.0))

            input_C_af['dedicated_chamber'] = int(data.get(f'dedicated_chamber{suffix}', 1)) == 2
            input_C_af['fixed_fin_direction'] = int(data.get(f'fixed_fin_direction{suffix}', 1)) == 2

        return cls(
            q_rtd=q_rtd, q_max=q_max, e_rtd=e_rtd,
            dualcompressor=dualcompressor, input_C_af=input_C_af
        )
