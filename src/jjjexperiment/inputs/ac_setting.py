from dataclasses import dataclass
from typing import Optional

import jjjexperiment.constants as jjj_consts
from jjjexperiment.inputs.options import 全般換気機能, 機器仕様手動入力タイプ


@dataclass
class AcSetting:
    """AC設定のピュアデータクラス"""
    
    mode: str
    type: Optional[str] = None
    input_mode: 機器仕様手動入力タイプ = 機器仕様手動入力タイプ.入力しない
    VAV: bool = False
    general_ventilation: bool = True
    f_SFP: float = 0.4 * 0.36
    duct_insulation: str = '全てもしくは一部が断熱区画外である'
    equipment_spec: str = '入力しない'
    V_hs_dsgn: float = 0.0
    
    # 機器仕様入力フィールド (初期値None)
    q_hs_rtd_input: Optional[float] = None
    P_hs_rtd_input: Optional[float] = None
    V_fan_rtd_input: Optional[float] = None
    P_fan_rtd_input: Optional[float] = None
    q_hs_mid_input: Optional[float] = None
    P_hs_mid_input: Optional[float] = None
    V_fan_mid_input: Optional[float] = None
    P_fan_mid_input: Optional[float] = None

    @classmethod
    def _parse_common_fields(cls, data: dict) -> dict:
        """共通フィールドのパース処理"""
        kwargs = {}
        
        # modeは子クラスで設定するため、ここでは設定しない
        
        if 'type' in data:
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

        # 入力モードをenumで設定
        if 'input' in data:
            kwargs['input_mode'] = 機器仕様手動入力タイプ(int(data['input']))

        if 'VAV' in data:
            kwargs['VAV'] = int(data['VAV']) == 2
        if 'general_ventilation' in data:
            kwargs['general_ventilation'] = int(data['general_ventilation']) == 全般換気機能.あり.value
        if 'input_f_SFP' in data and data['input_f_SFP'] == 2:
            kwargs['f_SFP'] = float(data['f_SFP'])

        if 'duct_insulation' in data:
            if data['duct_insulation'] == '全てもしくは一部が断熱区画外である' or int(data['duct_insulation']) == 1:
                kwargs['duct_insulation'] = '全てもしくは一部が断熱区画外である'
            elif str(data['duct_insulation']) == '全て断熱区画内である' or int(data['duct_insulation']) == 2:
                kwargs['duct_insulation'] = '全て断熱区画内である'
            else:
                raise ValueError('ダクトが通過する空間の入力が不正です。')

        if 'input_V_hs_dsgn' in data and int(data['input_V_hs_dsgn']) == 2:
            kwargs['V_hs_dsgn'] = float(data['V_hs_dsgn'])

        # 機器仕様入力フィールドを愚直にパース
        if 'q_hs_rtd' in data:
            kwargs['q_hs_rtd_input'] = float(data['q_hs_rtd'])
        if 'P_hs_rtd' in data:
            kwargs['P_hs_rtd_input'] = float(data['P_hs_rtd'])
        if 'V_fan_rtd' in data:
            kwargs['V_fan_rtd_input'] = float(data['V_fan_rtd'])
        if 'P_fan_rtd' in data:
            kwargs['P_fan_rtd_input'] = float(data['P_fan_rtd'])
        if 'q_hs_mid' in data:
            kwargs['q_hs_mid_input'] = float(data['q_hs_mid'])
        if 'P_hs_mid' in data:
            kwargs['P_hs_mid_input'] = float(data['P_hs_mid'])
        if 'V_fan_mid' in data:
            kwargs['V_fan_mid_input'] = float(data['V_fan_mid'])
        if 'P_fan_mid' in data:
            kwargs['P_fan_mid_input'] = float(data['P_fan_mid'])

        return kwargs
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AcSetting':
        """愚直なパース処理 - サフィックス不要"""
        kwargs = cls._parse_common_fields(data)
        
        # 基底クラスではデフォルトのmodeを設定
        if 'mode' not in kwargs:
            kwargs['mode'] = 'デフォルトモード'
        
        return cls(**kwargs)



class HeatingAcSetting(AcSetting):
    """暖房AC設定"""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HeatingAcSetting':
        # 親クラスのfrom_dictを呼び出し、modeを設定
        kwargs = cls._parse_common_fields(data)
        kwargs['mode'] = '住戸全体を連続的に暖房する方式'
        return cls(**kwargs)


class CoolingAcSetting(AcSetting):
    """冷房AC設定"""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CoolingAcSetting':
        # 親クラスのfrom_dictを呼び出し、modeを設定
        kwargs = cls._parse_common_fields(data)
        kwargs['mode'] = '住戸全体を連続的に冷房する方式'
        return cls(**kwargs)
