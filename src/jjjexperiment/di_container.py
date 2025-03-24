import pandas as pd
from dataclasses import dataclass
from injector import Injector, singleton, inject, provider, Module

# 【injector の基本】
# DIコンテナという考え方を行うためのライブラリ
# メソッド名は使用されない コンテナに入れるもの毎に型をキーとして定義する
# なんでも入れるわけではない、たびたび計算して更新されるものは入れない
# (どの行によるものか)追跡が難しくなるから
# いたるところで使用される設定値などをコンテナにまとめると
# 関数の引数が、前の計算から来ているものが中心になってよい
# DDDやクリーンアーキテクチャーで推奨されている

# 【DIコンテナ & グローバル変数 比較】
# DIコンテナ
# GOOD: 型で整理・差替え性能・テスト・
# BAD : 難しい・オーバーヘッド
# グローバル変数
# GOOD: 簡潔・一貫性
# BAD : 不明瞭な依存関係

# 【調べて分かったポイント】
# @provider: 注入するインスタンスの作成(ファクトリー)と取出しの設定を両方行う感覚
# なのでメソッド名は create-xxx() が分かりやすそう
# @provider & ->返却型 と同じ設定が binder.bind で可能
# どちらかがあれば十分
# 派生版:
# @provider & @singleton & ->返却型 == binder.bind(返却型, to=obj, scope=singleton)
# インスタンスを渡して初期化どちらもできるが、読みやすいのは binder の方かも
# @singleton を付けないとどうなるか、
# DIコンテナインスタンスを使いまわしている間はシングルトンが得られるが、
# DIコンテナインスタンス自体を再生成したときには中身はリセットされる

# 【おすすめ記事リスト】
# 分かる人が読めば、binder > provider > module の設定レベルの違いを解説していてよい
# https://zenn.dev/ktnyt/articles/cc5056ce81e9d3


@dataclass
class SampleHouseInfo:
    """家に関する設定値"""
    A_A: float
    """床面積の合計 [m2]"""
    A_MR: float
    """主たる居室の床面積 [m2]"""
    A_OR: float
    """その他の居室の床面積 [m2]"""
    r_A_ufvnt: float
    """当該住戸において、床下空間全体の面積に対する 換気を供給する床下空間の面積の比 [-]"""
    _r_A_ufac: float
    """当該住戸において、床下空間全体の面積に対する 空調を供給する床下空間の面積の比 [-]"""

    # getter
    @property
    def r_A_ufac(self): return self._r_A_ufac
    # setter
    @r_A_ufac.setter
    def r_A_ufac(self, r: float) -> None:
        """r_A_ufvnt を自動調整"""
        # 床下空調あるなら換気はしないので
        if (r is not None and r>0):
            self.r_A_ufvnt = 0
        self._r_A_ufac = r


class UfVarsDataFrame:
    '''床下空調 新ロジックの調査用 出力変数'''
    @inject
    def __init__(self):
        # d_t 長のデータフレーム
        self._df_d_t = pd.DataFrame()

    def update_df(self, data: dict):
        # 横連結時は ignore_index しないこと
        self._df_d_t = pd.concat([self._df_d_t, pd.DataFrame(data)], axis=1)

    def export_to_csv(self, filename: str, encoding: str = 'cp932'):
        '''csv書き出し'''
        self._df_d_t.to_csv(filename, index=False, encoding=encoding)


class HaCaInputHolder:
    """暖房時・冷房時の判別に使用したい"""
    @inject
    def __init__(self):
        self.__q_hs_rtd_C = None
        self.__q_hs_rtd_H = None

    @property
    def q_hs_rtd_C(self):
        return self.__q_hs_rtd_C
    @q_hs_rtd_C.setter
    def q_hs_rtd_C(self, value):
        self.__q_hs_rtd_C = value

    @property
    def q_hs_rtd_H(self):
        return self.__q_hs_rtd_H
    @q_hs_rtd_H.setter
    def q_hs_rtd_H(self, value):
        self.__q_hs_rtd_H = value

    def flg_char(self):
        if self.isH():
          ch_flg = '_H'
        elif self.isC():
          ch_flg = '_C'
        else:
          raise ValueError()
        return ch_flg

    # もう少し情報持たせてもよさそう
    def isH(self) -> bool:
        return (self.q_hs_rtd_H is not None) and (self.q_hs_rtd_C is None)
    def isC(self) -> bool:
        return (self.q_hs_rtd_C is not None) and (self.q_hs_rtd_H is None)


# DIコンテナの設定
class JJJExperimentModule(Module):
    @singleton
    @provider
    def provide_uf_vars_data_frame(self) -> UfVarsDataFrame:
        return UfVarsDataFrame()

    # NOTE: シングルトンを暖房用・冷房用に切替えるのは悪手、それぞれのインスタンスとする
    @singleton
    @provider
    def provide_ha_ca_input_holder(self) -> HaCaInputHolder:
        return HaCaInputHolder()

    # NOTE: providerが変数を受け取れるようにして
    # 動的な値でファクトリーしたかったができなかったので
    # モジュールクラスのメンバーとしてDI生成前にインスタンスを渡しています
    def set_houseinfo(self, house_info: SampleHouseInfo) -> None:
        self._house_info = house_info

    @singleton
    @provider
    def create_houseinfo(self) -> SampleHouseInfo:
        """注入するインスタンスを渡す"""
        # NOTE: ここの定義で、引数を利用できる方法が分からなかった
        return self._house_info

# NOTE: DIコンテナからの取得物への操作

# 関数の定義にinjectデコレータを使用し、DataFrameHolderインスタンスを受け取る
@inject
def some_function(data_frame_holder: UfVarsDataFrame):
    # 関数内で何らかの処理を行い、途中結果をデータフレームに追加
    intermediate_result = {'x': [1, 2, 3], 'y': [4, 5, 6]}  # 何らかの中間結果
    data_frame_holder.update_df(intermediate_result)

# ネストした関数の例
@inject
def another_function(data_frame_holder: UfVarsDataFrame):
    # 内部関数も同様にデータフレームを更新
    some_function(data_frame_holder)
