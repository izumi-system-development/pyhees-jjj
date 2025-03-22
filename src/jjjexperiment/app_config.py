from injector import Injector, singleton
# JJJ
from jjjexperiment.options import *

@singleton  # injector.get() したインスタンスの操作を共有するため
class AppConfig:
    def __init__(self):
        """規定値で初期化"""
        self.new_ufac_flg = 床下空調ロジック.変更しない.value
        """床下空調ロジック"""
        self.done_binsearch_new_ufac = False
        """床下空調新ロジック 二分探索完了"""

    def update(self, input: dict) -> None:
        """input.yaml から設定値を更新する"""
        if 'change_underfloor_temperature' in input:
            self.new_ufac_flg = int(input['change_underfloor_temperature'])

injector = Injector()
# NOTE: グローバルDIコンテナはベストではないが充分実用的なパターン

injector.binder.bind(
    AppConfig,
    to = AppConfig(),  # 規定値で初期化 後で上書き
    scope = singleton
)
