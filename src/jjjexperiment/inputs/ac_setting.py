from dataclasses import dataclass
from typing import Optional
# JJJ
from .options import 全般換気機能, 機器仕様手動入力タイプ, 暖房方式, 冷房方式, 計算モデル
# NOTE: データクラスからどうしてもロジックを参照するときは遅延インポートする

@dataclass
class AcSetting:
    """AC設定のピュアデータクラス"""

    mode: 暖房方式 | 冷房方式
    type: 計算モデル = 計算モデル.ダクト式セントラル空調機
    input_mode: 機器仕様手動入力タイプ = 機器仕様手動入力タイプ.入力しない
    equipment_spec: str = 機器仕様手動入力タイプ.入力しない.name
    """文字版"""

    VAV: bool = False
    general_ventilation: bool = True
    """全般換気"""
    # NOTE: enumもあるが現状はboolなので注意

    duct_insulation: str = '全てもしくは一部が断熱区画外である'

    V_hs_dsgn: float = 0.0
    """設計風量 [m3/h]"""
    f_SFP: float = 0.4 * 0.36
    """ファンの比消費電力"""

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
        # modeは子クラスで設定するため、ここでは設定しない
        kwargs = {}
        # 入力モードをenumで設定
        if 'type' in data:
            kwargs['type'] = 計算モデル(int(data['type']))
        if 'input' in data:
            input_mode = 機器仕様手動入力タイプ(int(data['input']))
            kwargs['input_mode'] = input_mode
            kwargs['equipment_spec'] = input_mode.name

        if 'VAV' in data:
            kwargs['VAV'] = int(data['VAV']) == 2
        if 'general_ventilation' in data:
            kwargs['general_ventilation'] = int(data['general_ventilation']) == 全般換気機能.あり.value

        if 'duct_insulation' in data:
            if data['duct_insulation'] == '全てもしくは一部が断熱区画外である' or int(data['duct_insulation']) == 1:
                kwargs['duct_insulation'] = '全てもしくは一部が断熱区画外である'
            elif str(data['duct_insulation']) == '全て断熱区画内である' or int(data['duct_insulation']) == 2:
                kwargs['duct_insulation'] = '全て断熱区画内である'
            else:
                raise ValueError('ダクトが通過する空間の入力が不正です。')

        if 'input_f_SFP' in data and data['input_f_SFP'] == 2:
            kwargs['f_SFP'] = float(data['f_SFP'])
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

        # 派生クラスを指定せずにインスタンスを作成しない
        # 常に H/C どちらか
        if 'mode' not in kwargs:
            raise ValueError

        return cls(**kwargs)


class HeatingAcSetting(AcSetting):
    """暖房AC設定"""

    @classmethod
    def from_dict(cls, data: dict) -> 'HeatingAcSetting':
        kwargs = cls._parse_common_fields(data)
        # NOTE: 暖房方式には他もあるが JJJ検証では対象としていない
        return cls(**kwargs, mode=暖房方式.住戸全体を連続的に暖房する方式)


class CoolingAcSetting(AcSetting):
    """冷房AC設定"""

    @classmethod
    def from_dict(cls, data: dict) -> 'CoolingAcSetting':
        kwargs = cls._parse_common_fields(data)
        # NOTE: 冷房方式には他もあるが JJJ検証では対象としていない
        return cls(**kwargs, mode=冷房方式.住戸全体を連続的に冷房する方式)
