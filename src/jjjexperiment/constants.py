from jjjexperiment.options import *

def version_info() -> str:
  """ 最終編集日をバージョン管理に使用します
  """
  # NOTE: subprocessモジュールによるコミット履歴からの生成は \
  # ipynb 環境では正常に動作しないことを確認しました(returned no-zero exit status 128.)
  return '_20240517'

# FIXME: このデコレータの定義箇所どこが最適か
# NOTE: 関数ラベリング用のデコレータ ex. @jjjexperiment_fork()
def jjjexperiment_clone(func):
  """ pyheesモジュール内における jjjexperimentによる 複製された実装"""
  return func
def jjjexperiment_mod(func):
  """ pyheesモジュール内における jjjexperimentによる 改変された実装"""
  return func


# FIXME: PROCESS_TYPE の置き場はこのファイル以外で最適な場所があれば移動する
PROCESS_TYPE_1 = 'ダクト式セントラル空調機'
PROCESS_TYPE_2 = 'ルームエアコンディショナ活用型全館空調（旧：現行省エネ法ルームエアコンモデル）'
PROCESS_TYPE_3 = 'ルームエアコンディショナ活用型全館空調（新：潜熱評価モデル）'
PROCESS_TYPE_4 = '電中研モデル'

Theta_hs_out_max_H_d_t_limit: float = 45
"""最大暖房出力時の熱源機の出口における空気温度の最大値の上限値"""
Theta_hs_out_min_C_d_t_limit: float = 15
"""最大冷房出力時の熱源機の出口における空気温度の最低値の下限値"""
C_df_H_d_t_defrost_ductcentral: float = 0.77
"""デフロストに関する暖房出力補正係数（ダクトセントラル空調機）"""
defrost_temp_ductcentral: float = 5
"""デフロスト発生外気温度（ダクトセントラル空調機）"""
defrost_humid_ductcentral: float = 80
"""デフロスト発生外気相対湿度（ダクトセントラル空調機）"""
phi_i: float = 0.49
"""ダクトiの線熱損失係数"""
C_V_fan_dsgn_H: float = 0.79
"""暖房時の送風機の設計風量に関する係数"""
C_V_fan_dsgn_C: float = 0.79
"""冷房時の送風機の設計風量に関する係数"""
C_df_H_d_t_defrost_rac: float = 0.77
"""デフロストに関する暖房出力補正係数（ルームエアコンディショナー）"""
defrost_temp_rac: float = 5
"""デフロスト発生外気温度（ルームエアコンディショナー）"""
defrost_humid_rac: float = 80
"""デフロスト発生外気相対湿度（ルームエアコンディショナー）"""
C_hm_C: float = 1.15
"""室内機吸い込み湿度に関する冷房出力補正係数"""
q_rtd_C_limit: float = 5600
"""定格冷房能力の最大値"""
change_supply_volume_before_vav_adjust: int = VAVありなしの吹出風量.数式を統一しない.value
"""VAV調整前の吹き出し風量の式を変更"""
change_heat_source_outlet_required_temperature: int = 1
"""熱源機の出口における空気温度"""
change_V_supply_d_t_i_max: int = Vサプライの上限キャップ.外さない.value
"""V_supply_d_t_iの上限キャップを外す"""
carry_over_heat: int = 過剰熱量繰越計算.行わない.value
"""過剰熱量を次の時刻に持ち越す"""
change_underfloor_temperature: int = 1
"""床下温度の計算式を変更"""

#以下、潜熱評価モデル追加対応(暖房)
A_f_hex_small_H: float = 0.2
"""定格冷却能力が5.6kW未満の場合のA_f,hex"""
A_e_hex_small_H: float = 6.2
"""定格冷却能力が5.6kW未満の場合のA_e,hex"""
A_f_hex_large_H: float = 0.3
"""定格冷却能力が5.6kW以上の場合のA_f,hex"""
A_e_hex_large_H: float = 10.6
"""定格冷却能力が5.6kW以上の場合のA_e,hex"""

a_r_H_t_t_a4: float = 0
"""コンプレッサ効率特性_a4"""
a_r_H_t_t_a3: float = 0
"""コンプレッサ効率特性_a3"""
a_r_H_t_t_a2: float = -0.0316
"""コンプレッサ効率特性_a2"""
a_r_H_t_t_a1: float = 0.2944
"""コンプレッサ効率特性_a1"""
a_r_H_t_t_a0: float = 0
"""コンプレッサ効率特性_a0"""
airvolume_minimum_H: float = 14.38995
"""風量特性_最小風量 [m3/min]"""
airvolume_maximum_H: float = 24.3824
"""風量特性_最大風量 [m3/min]"""
airvolume_coeff_a4_H: float = 0
"""風量特性_a4"""
airvolume_coeff_a3_H: float = 0
"""風量特性_a3"""
airvolume_coeff_a2_H: float = 0
"""風量特性_a2"""
airvolume_coeff_a1_H: float = 1.2946
"""風量特性_a1"""
airvolume_coeff_a0_H: float = 12.084
"""風量特性_a0"""
P_fan_H_d_t_a4: float = 0
"""ファン消費電力_a4"""
P_fan_H_d_t_a3: float = 1.4675
"""ファン消費電力_a3"""
P_fan_H_d_t_a2: float = -8.5886
"""ファン消費電力_a2"""
P_fan_H_d_t_a1: float = 20.217
"""ファン消費電力_a1"""
P_fan_H_d_t_a0: float = 50
"""ファン消費電力_a0"""
#以下、潜熱評価モデル追加対応(冷房)
A_f_hex_small_C: float = 0.2
"""定格冷却能力が5.6kW未満の場合のA_f,hex"""
A_e_hex_small_C: float = 6.2
"""定格冷却能力が5.6kW未満の場合のA_e,hex"""
A_f_hex_large_C: float = 0.3
"""定格冷却能力が5.6kW以上の場合のA_f,hex"""
A_e_hex_large_C: float = 10.6
"""定格冷却能力が5.6kW以上の場合のA_e,hex"""
a_c_hex_c_a4_C: float = 0
"""熱伝達特性_a4"""
a_c_hex_c_a3_C: float = 0
"""熱伝達特性_a3"""
a_c_hex_c_a2_C: float = 0
"""熱伝達特性_a2"""
a_c_hex_c_a1_C: float = 0.0631
"""熱伝達特性_a1"""
a_c_hex_c_a0_C: float = 0.0015
"""熱伝達特性_a0"""
a_r_C_t_t_a4: float = 0
"""コンプレッサ効率特性_a4"""
a_r_C_t_t_a3: float = 0
"""コンプレッサ効率特性_a3"""
a_r_C_t_t_a2: float = -0.0316
"""コンプレッサ効率特性_a2"""
a_r_C_t_t_a1: float = 0.2944
"""コンプレッサ効率特性_a1"""
a_r_C_t_t_a0: float = 0
"""コンプレッサ効率特性_a0"""
airvolume_minimum_C: float = 14.38995
"""風量特性_最小風量 [m3/min]"""
airvolume_maximum_C: float = 24.3824
"""風量特性_最大風量 [m3/min]"""
airvolume_coeff_a4_C: float = 0
"""風量特性_a4"""
airvolume_coeff_a3_C: float = 0
"""風量特性_a3"""
airvolume_coeff_a2_C: float = 0
"""風量特性_a2"""
airvolume_coeff_a1_C: float = 2.4855
"""風量特性_a1"""
airvolume_coeff_a0_C: float = 10.209
"""風量特性_a0"""
P_fan_C_d_t_a4: float = 0
"""ファン消費電力_a4"""
P_fan_C_d_t_a3: float = 1.4675
"""ファン消費電力_a3"""
P_fan_C_d_t_a2: float = 8.5886
"""ファン消費電力_a2"""
P_fan_C_d_t_a1: float = 20.217
"""ファン消費電力_a1"""
P_fan_C_d_t_a0: float = 50
"""ファン消費電力_a0"""

# 過剰熱量の持ち越し計算
Alpha_HCZ_i = [12.6, 12.6, 12.6, 12.6, 12.6]
"""区画i毎の壁床天井材の熱容量 [kJ・K]"""
Alpha_NR_i = 12.6
"""区画i毎の壁床天井材の熱容量 [kJ・K]"""
A_NR_R = 38.93
"""非居室の床面積[m2]"""  # NOTE: A_NR とは異なるものです

def set_constants(input: dict):
  """ 更新したい部分のみの辞書でも利用可能
  """
  if 'Theta_hs_out_max_H_d_t_limit' in input:
    global Theta_hs_out_max_H_d_t_limit
    Theta_hs_out_max_H_d_t_limit = float(input['Theta_hs_out_max_H_d_t_limit'])
  if 'Theta_hs_out_min_C_d_t_limit' in input:
    global Theta_hs_out_min_C_d_t_limit
    Theta_hs_out_min_C_d_t_limit = float(input['Theta_hs_out_min_C_d_t_limit'])
  if 'C_df_H_d_t_defrost_ductcentral' in input:
    global C_df_H_d_t_defrost_ductcentral
    C_df_H_d_t_defrost_ductcentral = float(input['C_df_H_d_t_defrost_ductcentral'])
  if 'defrost_temp_ductcentral' in input:
    global defrost_temp_ductcentral
    defrost_temp_ductcentral = float(input['defrost_temp_ductcentral'])
  if 'defrost_humid_ductcentral' in input:
    global defrost_humid_ductcentral
    defrost_humid_ductcentral = float(input['defrost_humid_ductcentral'])
  if 'phi_i' in input:
    global phi_i
    phi_i = float(input['phi_i'])
  if 'C_V_fan_dsgn_H' in input:
    global C_V_fan_dsgn_H
    C_V_fan_dsgn_H = float(input['C_V_fan_dsgn_H'])
  if 'C_V_fan_dsgn_C' in input:
    global C_V_fan_dsgn_C
    C_V_fan_dsgn_C = float(input['C_V_fan_dsgn_C'])
  if 'C_df_H_d_t_defrost_rac' in input:
    global C_df_H_d_t_defrost_rac
    C_df_H_d_t_defrost_rac = float(input['C_df_H_d_t_defrost_rac'])
  if 'defrost_temp_rac' in input:
    global defrost_temp_rac
    defrost_temp_rac = float(input['defrost_temp_rac'])
  if 'defrost_humid_rac' in input:
    global defrost_humid_rac
    defrost_humid_rac = float(input['defrost_humid_rac'])
  if 'C_hm_C' in input:
    global C_hm_C
    C_hm_C = float(input['C_hm_C'])
  if 'q_rtd_C_limit' in input:
    global q_rtd_C_limit
    q_rtd_C_limit = float(input['q_rtd_C_limit'])
  if 'R_g' in input:
    global R_g  # 地盤またはそれを覆う基礎の表面熱伝達抵抗 ((m2・K)/W) ex. 0.15
    R_g = float(input['R_g'])
  if 'change_supply_volume_before_vav_adjust' in input:
    global change_supply_volume_before_vav_adjust
    change_supply_volume_before_vav_adjust = int(input['change_supply_volume_before_vav_adjust'])
  if 'change_heat_source_outlet_required_temperature' in input:
    global change_heat_source_outlet_required_temperature
    change_heat_source_outlet_required_temperature = int(input['change_heat_source_outlet_required_temperature'])
  if 'change_V_supply_d_t_i_max' in input:
    global change_V_supply_d_t_i_max
    change_V_supply_d_t_i_max = int(input['change_V_supply_d_t_i_max'])
  if 'carry_over_heat' in input:
    global carry_over_heat
    carry_over_heat = int(input['carry_over_heat'])
  if 'change_underfloor_temperature' in input:
    global change_underfloor_temperature
    change_underfloor_temperature = int(input['change_underfloor_temperature'])
  #以下、潜熱評価モデル追加対応
  if 'H_A' in input:
    if 'A_f_hex_small' in input['H_A']:
      global A_f_hex_small_H
      A_f_hex_small_H = float(input['H_A']['A_f_hex_small'])
    if 'A_e_hex_small' in input['H_A']:
      global A_e_hex_small_H
      A_e_hex_small_H = float(input['H_A']['A_e_hex_small'])
    if 'A_f_hex_large' in input['H_A']:
      global A_f_hex_large_H
      A_f_hex_large_H = float(input['H_A']['A_f_hex_large'])
    if 'A_e_hex_large' in input['H_A']:
      global A_e_hex_large_H
      A_e_hex_large_H = float(input['H_A']['A_e_hex_large'])
    if 'compressor_coeff' in input['H_A']:
      global a_r_H_t_t_a4 
      a_r_H_t_t_a4 = float(input['H_A']['compressor_coeff'][0])
      global a_r_H_t_t_a3 
      a_r_H_t_t_a3 = float(input['H_A']['compressor_coeff'][1])
      global a_r_H_t_t_a2 
      a_r_H_t_t_a2 = float(input['H_A']['compressor_coeff'][2])
      global a_r_H_t_t_a1 
      a_r_H_t_t_a1 = float(input['H_A']['compressor_coeff'][3])
      global a_r_H_t_t_a0 
      a_r_H_t_t_a0 = float(input['H_A']['compressor_coeff'][4])
    if 'airvolume_minimum' in input['H_A']:
      global airvolume_minimum_H
      airvolume_minimum_H = float(input['H_A']['airvolume_minimum'])
    if 'airvolume_maximum' in input['H_A']:
      global airvolume_maximum_H
      airvolume_maximum_H = float(input['H_A']['airvolume_maximum'])
    if 'airvolume_coeff' in input['H_A']:
      global airvolume_coeff_a4_H 
      airvolume_coeff_a4_H = float(input['H_A']['airvolume_coeff'][0])
      global airvolume_coeff_a3_H 
      airvolume_coeff_a3_H = float(input['H_A']['airvolume_coeff'][1])
      global airvolume_coeff_a2_H 
      airvolume_coeff_a2_H = float(input['H_A']['airvolume_coeff'][2])
      global airvolume_coeff_a1_H 
      airvolume_coeff_a1_H = float(input['H_A']['airvolume_coeff'][3])
      global airvolume_coeff_a0_H 
      airvolume_coeff_a0_H = float(input['H_A']['airvolume_coeff'][4])
    if 'fan_coeff' in input['H_A']:
      global P_fan_H_d_t_a4 
      P_fan_H_d_t_a4 = float(input['H_A']['fan_coeff'][0])
      global P_fan_H_d_t_a3 
      P_fan_H_d_t_a3 = float(input['H_A']['fan_coeff'][1])
      global P_fan_H_d_t_a2 
      P_fan_H_d_t_a2 = float(input['H_A']['fan_coeff'][2])
      global P_fan_H_d_t_a1 
      P_fan_H_d_t_a1 = float(input['H_A']['fan_coeff'][3])
      global P_fan_H_d_t_a0 
      P_fan_H_d_t_a0 = float(input['H_A']['fan_coeff'][4])
  if 'C_A' in input:
    if 'A_f_hex_small' in input['C_A']:
      global A_f_hex_small_C
      A_f_hex_small_C = float(input['C_A']['A_f_hex_small'])
    if 'A_e_hex_small' in input['C_A']:
      global A_e_hex_small_C
      A_e_hex_small_C = float(input['C_A']['A_e_hex_small'])
    if 'A_f_hex_large' in input['C_A']:
      global A_f_hex_large_C
      A_f_hex_large_C = float(input['C_A']['A_f_hex_large'])
    if 'A_e_hex_large' in input['C_A']:
      global A_e_hex_large_C
      A_e_hex_large_C = float(input['C_A']['A_e_hex_large'])
    if 'heat_transfer_coeff' in input['C_A']:
      global a_c_hex_c_a4_C 
      a_c_hex_c_a4_C = float(input['C_A']['heat_transfer_coeff'][0])
      global a_c_hex_c_a3_C 
      a_c_hex_c_a3_C = float(input['C_A']['heat_transfer_coeff'][1])
      global a_c_hex_c_a2_C 
      a_c_hex_c_a2_C = float(input['C_A']['heat_transfer_coeff'][2])
      global a_c_hex_c_a1_C 
      a_c_hex_c_a1_C = float(input['C_A']['heat_transfer_coeff'][3])
      global a_c_hex_c_a0_C
      a_c_hex_c_a0_C = float(input['C_A']['heat_transfer_coeff'][4])
    if 'compressor_coeff' in input['C_A']:
      global a_r_C_t_t_a4 
      a_r_C_t_t_a4 = float(input['C_A']['compressor_coeff'][0])
      global a_r_C_t_t_a3 
      a_r_C_t_t_a3 = float(input['C_A']['compressor_coeff'][1])
      global a_r_C_t_t_a2 
      a_r_C_t_t_a2 = float(input['C_A']['compressor_coeff'][2])
      global a_r_C_t_t_a1 
      a_r_C_t_t_a1 = float(input['C_A']['compressor_coeff'][3])
      global a_r_C_t_t_a0 
      a_r_C_t_t_a0 = float(input['C_A']['compressor_coeff'][4])
    if 'airvolume_minimum' in input['C_A']:
      global airvolume_minimum_C
      airvolume_minimum_C = float(input['C_A']['airvolume_minimum'])
    if 'airvolume_maximum' in input['C_A']:
      global airvolume_maximum_C
      airvolume_maximum_C = float(input['C_A']['airvolume_maximum'])
    if 'airvolume_coeff' in input['C_A']:
      global airvolume_coeff_a4_C
      airvolume_coeff_a4_C = float(input['C_A']['airvolume_coeff'][0])
      global airvolume_coeff_a3_C 
      airvolume_coeff_a3_C = float(input['C_A']['airvolume_coeff'][1])
      global airvolume_coeff_a2_C 
      airvolume_coeff_a2_C = float(input['C_A']['airvolume_coeff'][2])
      global airvolume_coeff_a1_C 
      airvolume_coeff_a1_C = float(input['C_A']['airvolume_coeff'][3])
      global airvolume_coeff_a0_C 
      airvolume_coeff_a0_C = float(input['C_A']['airvolume_coeff'][4])
    if 'fan_coeff' in input['C_A']:
      global P_fan_C_d_t_a4 
      P_fan_C_d_t_a4 = float(input['C_A']['fan_coeff'][0])
      global P_fan_C_d_t_a3 
      P_fan_C_d_t_a3 = float(input['C_A']['fan_coeff'][1])
      global P_fan_C_d_t_a2 
      P_fan_C_d_t_a2 = float(input['C_A']['fan_coeff'][2])
      global P_fan_C_d_t_a1 
      P_fan_C_d_t_a1 = float(input['C_A']['fan_coeff'][3])
      global P_fan_C_d_t_a0 
      P_fan_C_d_t_a0 = float(input['C_A']['fan_coeff'][4])
