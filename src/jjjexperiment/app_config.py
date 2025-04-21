from injector import Injector, singleton

# JJJ
from jjjexperiment.options import *

@singleton  # injector.get() したインスタンスの操作を共有するため
class AppConfig:
    def __init__(self):
        """規定値で初期化"""

        # 熱源機ファン最低風量ユーザー入力(F24-02)
        self.input_V_hs_min_H: int = 最低風量直接入力.入力しない.value
        self.input_V_hs_min_C: int = 最低風量直接入力.入力しない.value

        # 床下空調新ロジック(F24-05)
        self.new_ufac_flg: int = 床下空調ロジック.変更しない.value
        """床下空調ロジック"""

    # 熱源機ファン最低風量ユーザー入力(F24-02)
    V_hs_min_H: float = None
    V_hs_min_C: float = None

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
        self.R_g = float(input['R_g'])
        # 熱源機ファン最低風量ユーザー入力(F24-02)
        if 'H_A' in input and 'input_V_hs_min_H' in input['H_A']:
            self.input_V_hs_min_H = int(input['H_A']['input_V_hs_min_H'])
            if self.input_V_hs_min_H == 最低風量直接入力.入力する.value:
                self.V_hs_min_H = int(input['H_A']['V_hs_min_H'])
        if 'C_A' in input and 'input_V_hs_min_C' in input['C_A']:
            self.input_V_hs_min_C = int(input['C_A']['input_V_hs_min_C'])
            if self.input_V_hs_min_C == 最低風量直接入力.入力する.value:
                self.V_hs_min_C = int(input['C_A']['V_hs_min_C'])

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
