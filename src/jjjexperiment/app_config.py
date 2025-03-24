from injector import Injector, singleton

# JJJ
from jjjexperiment.options import *

@singleton  # injector.get() したインスタンスの操作を共有するため
class AppConfig:
    def __init__(self):
        """規定値で初期化"""
        self.new_ufac_flg: int = 床下空調ロジック.変更しない.value
        """床下空調ロジック"""
        self.done_binsearch_new_ufac: bool = False
        """床下空調新ロジック 二分探索完了"""

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
        """input.yaml から設定値を更新する"""
        self.R_g = float(input['R_g'])
        # 床下空調新ロジック
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
