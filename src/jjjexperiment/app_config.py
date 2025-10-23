from dataclasses import dataclass
from injector import Injector, singleton

# JJJ
from jjjexperiment.options import *

@dataclass
class SeasonalSettings:
    """季節ごとの設定値"""
    general_ventilation: bool = True
    """全般換気の有無"""

    # [F25-01] 最低風量・最低電力 直接入力
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
    def heating_defaults(cls):
        return cls()

    @classmethod
    def cooling_defaults(cls):
        return cls()

    def update_from_input(self, input: dict):
        """inputオブジェクトから設定値を更新する"""
        # 熱源機ファン最低風量ユーザー入力(F24-02)
        if 'input_V_hs_min' in input:
            self.input_V_hs_min = 最低風量直接入力(int(input['input_V_hs_min']))

            if self.input_V_hs_min == 最低風量直接入力.入力する.value:
                # 事前条件: 有効な入力値が存在する
                if 'V_hs_min' not in input:
                    raise Exception('V_hs_min 最低風量の直接入力がありません.')
                self.V_hs_min = float(input['V_hs_min'])

                # NOTE: 最低電力直接入力は最低風量直接入力が有効なことが前提の仕様です
                if 'input_E_E_fan_min' in input:
                    self.input_E_E_fan_min = 最低電力直接入力(int(input['input_E_E_fan_min']))

                    if self.input_E_E_fan_min == 最低電力直接入力.入力する.value:
                        # 事前条件: 有効な入力値が存在する
                        if 'E_E_fan_min' not in input:
                            raise Exception('E_E_fan_min 最低電力の直接入力がありません.')
                        self.E_E_fan_min = float(input['E_E_fan_min'])

                        # 事前条件: 電力算定方法の指定あり
                        if 'E_E_fan_logic' not in input:
                            raise Exception('E_E_fan_logic ファン消費電力算定方法の指定がありません.')
                        self.E_E_fan_logic = ファン消費電力算定方法(int(input['E_E_fan_logic']))

# NOTE: singleton パターンを強調したクライアントコードでは
# 取得したインスタンスを使いまわすのではなく逐一 get() します.

@singleton  # injector.get() したインスタンスの操作を共有するため
class AppConfig:
    def __init__(self):
        """規定値で初期化"""
        self.H = SeasonalSettings().heating_defaults()
        self.C = SeasonalSettings().cooling_defaults()

        # 床下空調新ロジック(F24-05)
        self.new_ufac_flg: int = 床下空調ロジック.変更しない.value
        """床下空調ロジック"""

    # 床下空調新ロジック(F24-05)
    R_g: float = None
    """地盤またはそれを覆う基礎の表面熱伝達抵抗 [(m2・K)/W]"""
    Theta_g_avg: float = None
    """地盤内の不易層の温度 [℃]"""
    U_s_vert: float = None
    """床板(床チャンバー上面)の熱貫流率 [W/(m2・K)]"""
    phi: float = None
    """基礎(床チャンバー側面)の線熱貫流率 [W/(m・K)]"""

    # 大きくなったら関連するアップデートを分割定義する
    def update(self, input: dict) -> None:
        """inputオブジェクトから設定値を更新する"""
        if 'H_A' in input:
            self.H.update_from_input(input['H_A'])
        if 'C_A' in input:
            self.C.update_from_input(input['C_A'])

        self.R_g = float(input['R_g'])

        # 床下空調新ロジック(F24-05)
        if 'change_underfloor_temperature' in input:
            self.new_ufac_flg = int(input['change_underfloor_temperature'])
            if self.new_ufac_flg == 床下空調ロジック.変更する.value:
                if 'input_ufac_consts' in input:
                    self.is_valid_ufac_input = 2 == int(input['input_ufac_consts'])
                    if self.is_valid_ufac_input:
                        self.Theta_g_avg = float(input['Theta_g_avg'])
                        self.U_s_vert = float(input['U_s_vert'])
                        self.phi = float(input['phi'])

injector = Injector()
# NOTE: グローバルDIコンテナはベストではないが充分実用的なパターン

injector.binder.bind(
    AppConfig,
    to = AppConfig(),  # 規定値で初期化 後で上書き
    scope = singleton
)
