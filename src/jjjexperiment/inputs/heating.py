from dataclasses import dataclass
from typing import Optional

import pyhees.section4_2_b as dc_spec
import pyhees.section4_3_a as rac_spec

import jjjexperiment.constants as jjj_consts
from jjjexperiment.inputs.options import *

# TODO: 暖房・冷房を共通のベースクラスにして、calc_Q_UT_A の引数として使う

@dataclass
class SeasonalLoad:
    """暖房に関する設定値"""

    # NOTE: キー名は Heat/Cool 共通にする

    mode: str = '住戸全体を連続的に暖房する方式'

    type: Optional[str] = None
    q_hs_rtd: float = 0
    VAV: bool = False
    general_ventilation: bool = True

    f_SFP: float = 0.4 * 0.36
    """ファンの比消費電力"""

    duct_insulation: str = '全てもしくは一部が断熱区画外である'

    # Equipment specifications
    equipment_spec: str = '入力しない'
    q_hs_rtd: float = 0.0
    P_hs_rtd: float = 0.0
    V_fan_rtd: float = 0.0
    P_fan_rtd: float = 0.0
    q_hs_min: float = 0.0
    q_hs_mid: float = 0.0
    V_fan_mid: float = 0.0
    P_fan_mid: float = 0.0
    P_hs_mid: float = 0.0

    # Design air volume
    V_hs_dsgn: float = 0.0
    """設計風量 [m3/h]"""

    # Room heating equipment (currently not input-based)
    H_MR = None
    """主たる居室暖房機器"""
    H_OR = None
    """その他居室暖房機器"""
    H_HS = None
    """温水暖房の種類"""

    @classmethod
    def from_dict(cls, data: dict, region: int, A_A: float) -> 'SeasonalLoad':
        kwargs = {}
        if 'type' in data:
            # TODO: options の Enum へ移行予定
            match int(data['type']):
                case 1:
                    kwargs['type'] = jjj_consts.PROCESS_TYPE_1
                case 2:
                    kwargs['type'] = jjj_consts.PROCESS_TYPE_2
                case 3:
                    kwargs['type'] = jjj_consts.PROCESS_TYPE_3
                case 4:
                    kwargs['type'] = jjj_consts.PROCESS_TYPE_4
                case _:
                    raise ValueError

        if 'q_hs_rtd' in data:
            kwargs['q_hs_rtd'] = dc_spec.get_q_hs_rtd_H(region, A_A)
        if 'VAV' in data:
            kwargs['VAV'] = int(data['VAV']) == 2
        if 'general_ventilation' in data:
            kwargs['general_ventilation'] = int(data['general_ventilation']) == 全般換気機能.あり.value
        if 'input_f_SFP_H' in data and data['input_f_SFP_H'] == 2:
            kwargs['f_SFP'] = float(data['f_SFP_H'])

        # ダクトが通過する空間
        if 'duct_insulation' in data:
            if data['duct_insulation'] == '全てもしくは一部が断熱区画外である' or int(data['duct_insulation']) == 1:
                kwargs['duct_insulation'] = '全てもしくは一部が断熱区画外である'
            elif str(data['duct_insulation']) == '全て断熱区画内である' or int(data['duct_insulation']) == 2:
                kwargs['duct_insulation'] = '全て断熱区画内である'
            else:
                raise ValueError('ダクトが通過する空間の入力が不正です。')

        # 機器の仕様の入力
        if 'input' in data:
            input_mode = int(data['input'])
            if input_mode == 1:
                kwargs['equipment_spec'] = '入力しない'
                q_hs_rtd = dc_spec.get_q_hs_rtd_H(region, A_A)
                kwargs['q_hs_rtd'] = q_hs_rtd
                kwargs['P_hs_rtd'] = dc_spec.get_P_hs_rtd_H(q_hs_rtd)
                kwargs['V_fan_rtd'] = dc_spec.get_V_fan_rtd_H(q_hs_rtd)
                kwargs['P_fan_rtd'] = dc_spec.get_P_fan_rtd_H(kwargs['V_fan_rtd'])
                kwargs['q_hs_min'] = dc_spec.get_q_hs_min_H(q_hs_rtd)
                kwargs['q_hs_mid'] = dc_spec.get_q_hs_mid_H(q_hs_rtd)
                kwargs['V_fan_mid'] = dc_spec.get_V_fan_mid_H(kwargs['q_hs_mid'])
                kwargs['P_fan_mid'] = dc_spec.get_P_fan_mid_H(kwargs['V_fan_mid'])
                kwargs['P_hs_mid'] = float('nan')
            elif input_mode == 2:
                kwargs['equipment_spec'] = '定格能力試験の値を入力する'
                q_hs_rtd = float(data['q_hs_rtd_H'])
                kwargs['q_hs_rtd'] = q_hs_rtd
                kwargs['P_hs_rtd'] = float(data['P_hs_rtd_H'])
                kwargs['V_fan_rtd'] = float(data['V_fan_rtd_H'])
                kwargs['P_fan_rtd'] = float(data['P_fan_rtd_H'])
                kwargs['q_hs_min'] = dc_spec.get_q_hs_min_H(q_hs_rtd)
                kwargs['q_hs_mid'] = dc_spec.get_q_hs_mid_H(q_hs_rtd)
                kwargs['V_fan_mid'] = dc_spec.get_V_fan_mid_H(kwargs['q_hs_mid'])
                kwargs['P_fan_mid'] = dc_spec.get_P_fan_mid_H(kwargs['V_fan_mid'])
                kwargs['P_hs_mid'] = float('nan')
            elif input_mode == 3:
                kwargs['equipment_spec'] = '定格能力試験と中間能力試験の値を入力する'
                q_hs_rtd = float(data['q_hs_rtd_H'])
                kwargs['q_hs_rtd'] = q_hs_rtd
                kwargs['P_hs_rtd'] = float(data['P_hs_rtd_H'])
                kwargs['V_fan_rtd'] = float(data['V_fan_rtd_H'])
                kwargs['P_fan_rtd'] = float(data['P_fan_rtd_H'])
                kwargs['q_hs_min'] = dc_spec.get_q_hs_min_H(q_hs_rtd)
                kwargs['q_hs_mid'] = float(data['q_hs_mid_H'])
                kwargs['V_fan_mid'] = float(data['V_fan_mid_H'])
                kwargs['P_hs_mid'] = float(data['P_hs_mid_H'])
                kwargs['P_fan_mid'] = float(data['P_fan_mid_H'])
            elif input_mode == 4:
                # NOTE: Input mode 4 (RAC specifications) handled by DenchuRacSpecification
                kwargs['equipment_spec'] = '最小・定格・最大出力時のメーカー公表値を入力する'
            else:
                raise ValueError('機器の仕様の入力が不正です。')

        # 設計風量
        if 'input_V_hs_dsgn_H' in data and int(data['input_V_hs_dsgn_H']) == 2:
            kwargs['V_hs_dsgn'] = float(data['V_hs_dsgn_H'])

        return cls(**kwargs)

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
