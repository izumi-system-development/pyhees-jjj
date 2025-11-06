from dataclasses import dataclass
from typing import Optional

import pyhees.section4_2_b as dc_spec
import pyhees.section4_3_a as rac_spec

import jjjexperiment.constants as jjj_consts
from jjjexperiment.inputs.options import *

@dataclass
class SeasonalLoad:
    """冷房に関する設定値"""

    # NOTE: キー名は Heat/Cool 共通にする
    # 親で H/C 分かれているのでフィールドに _H/_C 不要

    mode: str = '住戸全体を連続的に冷房する方式'

    type: Optional[str] = None
    q_hs_rtd: float = 0
    VAV: bool = False
    general_ventilation: bool = True
    """全般換気"""
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

    V_hs_dsgn: float = 0.0
    """設計風量 [m3/h]"""

    # RAC specifications for type 4
    q_rac_min: float = 0.0
    q_rac_rtd: float = 0.0
    q_rac_max: float = 0.0
    P_rac_min: float = 0.0
    P_rac_rtd: float = 0.0
    P_rac_max: float = 0.0
    V_rac_inner: float = 0.0
    V_rac_outer: float = 0.0
    Theta_RH_rac_inner_pub: float = 0.0
    Theta_RH_rac_outer_pub: float = 0.0
    RH_rac_inner_pub: float = 0.0
    RH_rac_outer_pub: float = 0.0

    # Room cooling equipment (currently not input-based)
    C_MR = None
    """主たる居室冷房機器"""
    C_OR = None
    """その他居室冷房機器"""

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

        if 'VAV' in data:
            kwargs['VAV'] = int(data['VAV']) == 2
        if 'general_ventilation' in data:
            kwargs['general_ventilation'] = int(data['general_ventilation']) == 全般換気機能.あり.value
        if 'input_f_SFP_C' in data and data['input_f_SFP_C'] == 2:
            kwargs['f_SFP'] = float(data['f_SFP_C'])

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
                q_hs_rtd = dc_spec.get_q_hs_rtd_C(region, A_A)
                kwargs['q_hs_rtd'] = q_hs_rtd
                kwargs['q_hs_mid'] = dc_spec.get_q_hs_mid_C(q_hs_rtd)
                kwargs['q_hs_min'] = dc_spec.get_q_hs_min_C(q_hs_rtd)
                kwargs['P_hs_rtd'] = dc_spec.get_P_hs_rtd_C(q_hs_rtd)
                kwargs['V_fan_rtd'] = dc_spec.get_V_fan_rtd_C(q_hs_rtd)
                kwargs['V_fan_mid'] = dc_spec.get_V_fan_mid_C(kwargs['q_hs_mid'])
                kwargs['P_fan_rtd'] = dc_spec.get_P_fan_rtd_C(kwargs['V_fan_rtd'])
                kwargs['P_fan_mid'] = dc_spec.get_P_fan_mid_C(kwargs['V_fan_mid'])
                kwargs['P_hs_mid'] = float('nan')
            elif input_mode == 2:
                kwargs['equipment_spec'] = '定格能力試験の値を入力する'
                q_hs_rtd = float(data['q_hs_rtd_C'])
                kwargs['q_hs_rtd'] = q_hs_rtd
                kwargs['P_hs_rtd'] = float(data['P_hs_rtd_C'])
                kwargs['V_fan_rtd'] = float(data['V_fan_rtd_C'])
                kwargs['P_fan_rtd'] = float(data['P_fan_rtd_C'])
                kwargs['q_hs_mid'] = dc_spec.get_q_hs_mid_C(q_hs_rtd)
                kwargs['q_hs_min'] = dc_spec.get_q_hs_min_C(q_hs_rtd)
                kwargs['V_fan_mid'] = dc_spec.get_V_fan_mid_C(kwargs['q_hs_mid'])
                kwargs['P_fan_mid'] = dc_spec.get_P_fan_mid_C(kwargs['V_fan_mid'])
                kwargs['P_hs_mid'] = float('nan')
            elif input_mode == 3:
                kwargs['equipment_spec'] = '定格能力試験と中間能力試験の値を入力する'
                q_hs_rtd = float(data['q_hs_rtd_C'])
                kwargs['q_hs_rtd'] = q_hs_rtd
                kwargs['P_hs_rtd'] = float(data['P_hs_rtd_C'])
                kwargs['V_fan_rtd'] = float(data['V_fan_rtd_C'])
                kwargs['P_fan_rtd'] = float(data['P_fan_rtd_C'])
                kwargs['q_hs_mid'] = float(data['q_hs_mid_C'])
                kwargs['P_hs_mid'] = float(data['P_hs_mid_C'])
                kwargs['V_fan_mid'] = float(data['V_fan_mid_C'])
                kwargs['P_fan_mid'] = float(data['P_fan_mid_C'])
                kwargs['q_hs_min'] = dc_spec.get_q_hs_min_C(q_hs_rtd)
            elif input_mode == 4:
                kwargs['equipment_spec'] = '最小・定格・最大出力時のメーカー公表値を入力する'
                kwargs['q_rac_min'] = float(data['q_rac_min_C'])
                kwargs['q_rac_rtd'] = float(data['q_rac_rtd_C'])
                kwargs['q_rac_max'] = float(data['q_rac_max_C'])
                kwargs['P_rac_min'] = float(data['P_rac_min_C'])
                kwargs['P_rac_rtd'] = float(data['P_rac_rtd_C'])
                kwargs['P_rac_max'] = float(data['P_rac_max_C'])
                kwargs['V_rac_inner'] = float(data['V_rac_inner_C'])
                kwargs['V_rac_outer'] = float(data['V_rac_outer_C'])
                kwargs['Theta_RH_rac_inner_pub'] = float(data['Theta_RH_rac_inner_pub_C'])
                kwargs['Theta_RH_rac_outer_pub'] = float(data['Theta_RH_rac_outer_pub_C'])
                kwargs['RH_rac_inner_pub'] = float(data['RH_rac_inner_pub_C'])
                kwargs['RH_rac_outer_pub'] = float(data['RH_rac_outer_pub_C'])
            else:
                raise ValueError('機器の仕様の入力が不正です。')

        # 設計風量
        if 'input_V_hs_dsgn_C' in data and int(data['input_V_hs_dsgn_C']) == 2:
            kwargs['V_hs_dsgn'] = float(data['V_hs_dsgn_C'])

        return cls(**kwargs)

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
        if data.get('type') == 2 and int(data.get('input_rac_performance', 1)) == 2:
            q_rtd = float(data['q_rac_rtd_C'])
            q_max = float(data['q_rac_max_C'])
            e_rtd = float(data['e_rac_rtd_C'])
        elif data.get('type') == 4:
            q_rtd = float(data['q_rac_pub_rtd']) * 1000
            q_max = float(data['q_rac_pub_max']) * 1000
            e_rtd = rac_spec.get_e_rtd_C(e_class, q_rtd)
        else:
            q_rtd = rac_spec.get_q_rtd_C(A_A)
            q_max = rac_spec.get_q_max_C(q_rtd)
            e_rtd = rac_spec.get_e_rtd_C(e_class, q_rtd)

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
