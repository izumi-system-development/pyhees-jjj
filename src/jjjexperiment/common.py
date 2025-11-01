from enum import Enum
from typing import Annotated
import numpy as np
from numpy.typing import NDArray

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
