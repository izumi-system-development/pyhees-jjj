from dataclasses import dataclass
from injector import Injector, singleton
# JJJ
from jjjexperiment.inputs.options import *

# NOTE: singleton パターンを強調したクライアントコードでは
# 取得したインスタンスを使いまわすのではなく逐一 get() します.

@singleton  # injector.get() したインスタンスの操作を共有するため
class AppConfig:
    def __init__(self):
        """規定値で初期化"""

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

# injector.binder.bind(
#     AppConfig,
#     to = AppConfig(),  # 規定値で初期化 後で上書き
#     scope = singleton
# )
