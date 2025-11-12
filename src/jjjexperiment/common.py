from enum import Enum
from typing import Annotated, Optional
from injector import Injector
import numpy as np
from numpy.typing import NDArray

# NOTE: どこからでも利用するのでカスタムファイルへ依存させない
# 循環参照の原因になるため

# WARNING: np.shape のアサートには残念ながら使用できない
Array5 = Annotated[NDArray[np.float64], '5']
Array5x1 = Annotated[NDArray[np.float64], '5x1']
Array5x8760 = Annotated[NDArray[np.float64], '5x8760']
Array12 = Annotated[NDArray[np.float64], '12']
Array12x1 = Annotated[NDArray[np.float64], '12x1']
Array12x8760 = Annotated[NDArray[np.float64], '12x8760']
Array8760 = Annotated[NDArray[np.float64], '8760']
# これ以外のその他変則的な次元はその場で定義

class JJJ_HCM(Enum):
  """暖冷房期間"""
  Undefined = 0  # Enumの規定値無効化

  H = 1  # 暖房期
  C = 2  # 冷房期
  M = 3  # 中間期

# NOTE: オリジンが更新されたときに改変コードの追従対応の判断用にラベリングしている

def jjj_cloning(func):
  """ pyheesモジュール内の関数を jjjexperimentにより 複製改変したもの"""
  return func

def jjj_cloned(func):
  """ pyheesモジュール内における jjjexperimentによる 複製改変されたもの"""
  # NOTE: オリジナルには手を加えない
  return func

def jjj_mod(func):
  """ pyheesモジュール内における jjjexperimentによる 改変された実装"""
  # NOTE: オリジナルに手を加え 複製はしない
  return func

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
