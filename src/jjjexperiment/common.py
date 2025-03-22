from enum import Enum

# NOTE: import * して利用するので、jjj_ 付けるとわかりやすい

class JJJ_HCM(Enum):
  """暖冷房期間"""
  Undefined = 0  # Enumの規定値無効化

  H = 1  # 暖房期
  C = 2  # 冷房期
  M = 3  # 中間期

class JJJ_PROC_TYPE(Enum):
  """処理方式"""
  Undefined = 0  # Enum規定値無効

  ダクト式セントラル空調機 = 1
  RAC活用型全館空調_現行省エネ法RACモデル = 2  # 旧ロジック
  RAC活用型全館空調_潜熱評価モデル = 3  # 新ロジック
  電中研モデル = 4

class JJJ_SpecInput(Enum):
  """機器仕様の手動入力タイプ"""
  Undefined = 0  # Enum規定値無効

  入力しない = 1
  定格能力試験の値を入力する = 2
  定格能力試験と中間能力試験の値を入力する = 3
  最小_定格_最大出力時のメーカー公表値を入力する = 4

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
