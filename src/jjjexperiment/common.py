from enum import Enum

# NOTE: import * して利用するので、jjj_ 付けるとわかりやすい

class JJJ_HCM(Enum):
    H = 1  # 暖房期
    C = 2  # 冷房期
    M = 3  # 中間期

# NOTE: 関数ラベリング用のデコレータ ex. @jjjexperiment_fork()
def jjj_clone(func):
  """ pyheesモジュール内における jjjexperimentによる 複製された実装"""
  return func

def jjj_mod(func):
  """ pyheesモジュール内における jjjexperimentによる 改変された実装"""
  return func
