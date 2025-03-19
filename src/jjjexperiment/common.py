from enum import Enum

# NOTE: import * して利用するので、jjj_ 付けるとわかりやすい

class JJJ_HCM(Enum):
    H = 1  # 暖房期
    C = 2  # 冷房期
    M = 3  # 中間期

# NOTE: オリジンが更新されたときに改変コードの追従対応の判断用にラベリングしている

def jjj_cloning(func):
  """ pyheesモジュール内の関数を jjjexperimentにより 複製改変したもの"""
  return func

def jjj_cloned(func):
  """ pyheesモジュール内における jjjexperimentによる 複製改変されたもの"""
  return func

def jjj_mod(func):
  """ pyheesモジュール内における jjjexperimentによる 改変された実装"""
  return func
