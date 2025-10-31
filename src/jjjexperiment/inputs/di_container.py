from typing import NewType, Optional
from injector import Injector, singleton, provider, Module
# JJJ 共通
from jjjexperiment.inputs.options import *
import jjjexperiment.inputs.common as common_input
import jjjexperiment.inputs.cooling as common_cooling_input
import jjjexperiment.inputs.heating as common_heating_input
# F23 電中研モデル
import jjjexperiment.denchu.inputs.heating as denchu_heating_input
import jjjexperiment.denchu.inputs.cooling as denchu_cooling_input
# F24-05 新床下空調
import jjjexperiment.underfloor_ac.inputs.common as ufac_input
# F25-01 最小風量・最低電力 直接入力
import jjjexperiment.ac_min_volume_input.inputs.heating as v_min_heating_input
import jjjexperiment.ac_min_volume_input.inputs.cooling as v_min_cooling_input

# NOTE: Injector はフルパスでクラス名を判別するためファイル自体が同名でも問題ない

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

# DI用の型エイリアス
# NOTE: 単一クラスをわざわざデータクラス化するのを回避できる
TestMode = NewType('TestMode', bool)
CaseName = NewType('CaseName', str)
LoadFile = NewType('LoadFile', str)
ClimateFile = NewType('ClimateFile', str)

def create_injector_from_json(input_data: dict, test_mode: bool = False) -> Injector:
    """ファクトリーメソッド"""
    module = JJJExperimentModule(input_data, test_mode)
    injector = Injector([module])
    # NOTE: injector自身をinjectするパターンを採用しました
    # 計算過程で後付けで bind したり、文脈を分岐させることができる(Heat/Coolの切替に使用)
    module._injector = injector
    return injector

# ネストされた関数からの取得用
# NOTE: injectの連鎖でも到達できない深いネストの時
# (グローバルDIコンテナーは回避した)
# ContextManager にする方法もあるが今は簡易性を優先
import threading
_current_injector = threading.local()
def set_current_injector(injector: Injector):
    """スレッドにDIコンテキストをセット"""
    _current_injector.value = injector

def get_current_injector() -> Optional[Injector]:
    """スレッドからDIコンテキストを取得"""
    return getattr(_current_injector, 'value', None)

def clear_current_injector():
    """スレッドにセットしたDIコンテキストをリセット"""
    if hasattr(_current_injector, 'value'):
        delattr(_current_injector, 'value')

# DIコンテナの設定
class JJJExperimentModule(Module):
    def __init__(self, input: dict = None, test_mode: bool = False):
        """inputオブジェクトから設定値を更新する"""
        # メンバー変数
        self._input = input
        self._test_mode = test_mode
        self._injector = None  # lateinit

        self._validate_and_update_inputs()

    def _validate_and_update_inputs(self):
        """データクラスを跨いだ整合性のロジック"""
        # まだプロバイダーは使用しない書き方にする(できるけど)
        new_ufac_flg = self._input.get('change_underfloor_temperature', None)
        old_ufac_flg = self._input.get('underfloor_air_conditioning_air_supply', None)
        if new_ufac_flg is not None and int(new_ufac_flg) == 床下空調ロジック.変更する.value:
            # 新床下空調
            self._input['r_A_ufac'] = 100.0  # [%] WG資料より
            self._input['underfloor_air_conditioning_air_supply'] = 2  # 従来床下空調を含む
            # 後はデータクラス内で > 床下換気ナシ & 床下断熱状態
        elif old_ufac_flg is not None and int(old_ufac_flg) == 2:
            # 従来の床下空調
            self._input['r_A_ufac'] = common_input.OuterSkin.YUCACO_r_A_ufvnt / 100.0  # [%]
            self._input['underfloor_air_conditioning_air_supply'] = 2
            # 後はデータクラス内で > 床下換気ナシ & 床下断熱状態
        else:
            # 非床下空調
            if 'r_A_ufvnt' in self._input:
                self._input['r_A_ufac'] = self._input.get('r_A_ufvnt', None)
            else:
                raise KeyError('r_A_ufvnt が設定されていません')

    @singleton
    @provider
    def provide_injector(self) -> Injector:
        return self._injector
    # NOTE: Injector 自身の注入は 通常のDI利用ケースでは必須ではないが本プロジェクトでは使用しています

    @singleton
    @provider
    def provide_test_mode(self) -> TestMode: return TestMode(self._test_mode)
    @singleton
    @provider
    def provide_case_name(self) -> CaseName: return CaseName(self._input.get('case_name', 'default'))
    @singleton
    @provider
    def provide_climate_file(self) -> ClimateFile: return ClimateFile(self._input.get('climateFile', '-'))
    @singleton
    @provider
    def provide_load_file(self) -> LoadFile: return LoadFile(self._input.get('loadFile', '-'))
    # TODO: climateFile, loadFile のケース統一する

    @singleton
    @provider
    def create_houseinfo(self) -> common_input.HouseInfo:
        return common_input.HouseInfo.from_dict(self._input if self._input is not None else {})
    @singleton
    @provider
    def provide_outer_skin(self) -> common_input.OuterSkin:
        return common_input.OuterSkin.from_dict(self._input if self._input is not None else {})
    @singleton
    @provider
    def provide_heatexchangeventilation(self) -> common_input.HEX:
        return common_input.HEX.from_dict(self._input if self._input is not None else {})

    @singleton
    @provider
    def provide_common_heating_input(self) -> common_heating_input.SeasonalLoad:
        house_info = self.create_houseinfo()
        return common_heating_input.SeasonalLoad \
            .from_dict(
                self._input['H_A'] if self._input is not None and 'H_A' in self._input else {},
                house_info.region,
                house_info.A_A)
    @singleton
    @provider
    def provide_common_cooling_input(self) -> common_cooling_input.SeasonalLoad:
        house_info = self.create_houseinfo()
        return common_cooling_input.SeasonalLoad \
            .from_dict(
                self._input['C_A'] if self._input is not None and 'C_A' in self._input else {},
                house_info.region,
                house_info.A_A)

    @singleton
    @provider
    def provide_common_cooling_crac_input(self) -> common_cooling_input.CRACSpecification:
        house_info = self.create_houseinfo()
        return common_cooling_input.CRACSpecification \
            .from_dict(
                self._input['C_A'] if self._input is not None and 'C_A' in self._input else {},
                house_info.A_A)
    @singleton
    @provider
    def provide_common_heating_crac_input(self) -> common_heating_input.CRACSpecification:
        cool_crac_input = self.provide_common_cooling_crac_input()
        return common_heating_input.CRACSpecification \
            .from_dict(
                self._input['H_A'] if self._input is not None and 'H_A' in self._input else {},
                # NOTE: ルームエアコン冷房情報を使用する
                cool_crac_input.q_rtd, cool_crac_input.q_max, cool_crac_input.e_rtd)

    # 電中研モデル
    @singleton
    @provider
    def provide_denchu_catalog_heating_input(self) -> denchu_heating_input.DenchuCatalogSpecification:
        return denchu_heating_input.DenchuCatalogSpecification \
            .from_dict(self._input['H_A'] if self._input is not None and 'H_A' in self._input else {})
    @singleton
    @provider
    def provide_denchu_catalog_cooling_input(self) -> denchu_cooling_input.DenchuCatalogSpecification:
        return denchu_cooling_input.DenchuCatalogSpecification \
            .from_dict(self._input['C_A'] if self._input is not None and 'C_A' in self._input else {})

    # F24-05 新・床下空調
    @provider
    def provide_underfloor_ac_input(self) -> ufac_input.UnderfloorAc:
        return ufac_input.UnderfloorAc.from_dict(self._input if self._input is not None else {})
    @singleton
    @provider
    def provide_uf_vars_data_frame(self) -> ufac_input.UfVarsDataFrame:
        return ufac_input.UfVarsDataFrame()

    # F25-01 最小風量・最低電力 直接入力
    @singleton
    @provider
    def provide_v_min_heating_input(self) -> v_min_heating_input.InputMinVolumeInput:
        return v_min_heating_input.InputMinVolumeInput \
            .from_dict(self._input['H_A'] if self._input is not None and 'H_A' in self._input else {})
    @singleton
    @provider
    def provide_v_min_cooling_input(self) -> v_min_cooling_input.InputMinVolumeInput:
        return v_min_cooling_input.InputMinVolumeInput \
            .from_dict(self._input['C_A'] if self._input is not None and 'C_A' in self._input else {})
