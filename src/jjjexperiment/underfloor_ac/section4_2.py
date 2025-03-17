from nptyping import Float64, NDArray, Shape
import numpy as np
from injector import Injector

import pyhees.section3_1 as ld
import pyhees.section3_1_e as algo
import pyhees.section3_2 as gihi
import pyhees.section4_2 as dc
import pyhees.section11_1 as rgn
import pyhees.section11_2 as slr
# JJJ
import jjjexperiment.constants as jjj_consts
from jjjexperiment.di_container import *
from jjjexperiment.common import *
from jjjexperiment.options import *
from jjjexperiment.logger import LimitedLoggerAdapter as _logger, log_res

def calc_Theta_uf(
        L_H_flr1st: float,
        A_s_ufvnt: float,
        Theta_in: float,
        Theta_ex: float,
        V_flr1st: float,
        ) -> float:
    """床下空間の温度 (40-4) 単時点

    Args:
        L_H_flr1st: 一階部分の1時間当たりの暖房負荷 [MJ/h]
        A_s_ufvnt: 空気を供給する床下空間に接する床の面積 [m2]
        Theta_in: 室温 [℃]
        Theta_ex: 外気温度 [℃]
        V_flr1st: 第1床面積 [m2]
    Returns:
        床下空間の温度 [℃]
    """
    ro_air = dc.get_ro_air()    # 空気密度 [kg/m3]
    c_p_air = algo.get_c_p_air()  # 空気の比熱 [kJ/kgK]
    U_s = dc.get_U_s()          # 床の熱貫流率 [W/m2K]

    H_floor = 0.7  # 床の温度差係数(-) 損失として

    a1 = L_H_flr1st * 1e+3
    a2 = U_s * A_s_ufvnt * (Theta_in - Theta_ex) * H_floor * 3.6
    a3 = Theta_in * (ro_air * c_p_air * V_flr1st + U_s * A_s_ufvnt * 3.6)
    b1 = ro_air * c_p_air * V_flr1st + U_s * A_s_ufvnt * 3.6

    Theta_uf = (a1 - a2 + a3) / b1
    return Theta_uf

@jjj_clone
@log_res(['L_star_newuf_H_d_t_i'])
def get_L_star_newuf_H_d_t_i(L_H_d_t_i, Q_star_trs_prt_d_t_i, region,
                       A_A, A_MR, A_OR, Q, r_A_ufac, underfloor_insulation, Theta_uf_d_t_i, Theta_ex_d_t,
                       V_dash_supply_d_t_i, L_dash_H_R_d_t, L_dash_CS_R_d_t, Theta_star_HBR_d_t, R_g, di: Injector = None):
    """(8-1)(8-2)(8-3)

    Args:
      L_H_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの暖房負荷（MJ/h）
      Q_star_trs_prt_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの熱損失を含む負荷バランス時の非居室への熱移動（MJ/h）
      region: 地域区分

      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      r_A_ufac(float): 当該住戸において、床下空間全体の面積に対する 空調空気を供給する床下空間の面積の比 (-)
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      Theta_uf_d_t_i(ndarray): 床下空間の空気の温度 (℃)
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      V_dash_supply_d_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iのVAV調整前の熱源機の風量（m3/h）
      L_dash_H_R_d_t(ndarray): 標準住戸の負荷補正前の暖房負荷 (MJ/h)
      L_dash_CS_R_d_t(ndarray): 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）
      R_g: 地盤またはそれを覆う基礎の表面熱伝達抵抗 ((m2・K)/W)

    Returns:
      日付dの時刻tにおける暖冷房区画iの1時間当たりの熱損失を含む負荷バランス時の暖房負荷 [MJ/h]

    """
    # 事前条件: 床下空調 新ロジックのみで使用
    assert jjj_consts.change_underfloor_temperature == 床下空調ロジック.変更する.value, \
      "床下空調 新ロジックのみで使用すべきロジックです."

    L_normal_uf2room_d_t_i, L_newuf2room_d_t_i, L_uf2outdoor_d_t_i, L_uf2gnd_d_t_i, Theta_uf_supply_d_t \
      = get_delta_L_star_newuf(
        region, A_A, A_MR, A_OR, Q, r_A_ufac, underfloor_insulation, Theta_uf_d_t_i, Theta_ex_d_t,
        V_dash_supply_d_t_i, L_dash_H_R_d_t, L_dash_CS_R_d_t, Theta_star_HBR_d_t, R_g, di)

    # θ_supply_d_t の逆算は一度しか行わないため
    jjj_consts.done_binsearch_newufac = True

    if di is not None:
      hci = di.get(HaCaInputHolder)
      df_holder = di.get(UfVarsDataFrame)
      df_holder.update_df({
          f"L_uf2room{hci.flg_char()}_1": L_normal_uf2room_d_t_i[0],
          f"L_uf2room{hci.flg_char()}_2": L_normal_uf2room_d_t_i[1],
          f"L_uf2room{hci.flg_char()}_3": L_normal_uf2room_d_t_i[2],
          f"L_uf2room{hci.flg_char()}_4": L_normal_uf2room_d_t_i[3],
          f"L_uf2room{hci.flg_char()}_5": L_normal_uf2room_d_t_i[4],
          f"L_uf2outdoor{hci.flg_char()}_1": L_uf2outdoor_d_t_i[0],
          f"L_uf2outdoor{hci.flg_char()}_2": L_uf2outdoor_d_t_i[1],
          f"L_uf2outdoor{hci.flg_char()}_3": L_uf2outdoor_d_t_i[2],
          f"L_uf2outdoor{hci.flg_char()}_4": L_uf2outdoor_d_t_i[3],
          f"L_uf2outdoor{hci.flg_char()}_5": L_uf2outdoor_d_t_i[4],
          f"L_uf2gnd{hci.flg_char()}_1": L_uf2gnd_d_t_i[0],
          f"L_uf2gnd{hci.flg_char()}_2": L_uf2gnd_d_t_i[1],
          f"L_uf2gnd{hci.flg_char()}_3": L_uf2gnd_d_t_i[2],
          f"L_uf2gnd{hci.flg_char()}_4": L_uf2gnd_d_t_i[3],
          f"L_uf2gnd{hci.flg_char()}_5": L_uf2gnd_d_t_i[4],
        })

    H, C, M = dc.get_season_array_d_t(region)
    Hf = np.logical_and(H, L_H_d_t_i[:5] > 0)

    # NOTE: 床下→居室全体 の熱負荷補正については足しなおしていない
    # (L_newuf2room_d_t_i 不使用)

    L_star_H_d_t_i = np.zeros((5, 24 * 365))
    L_star_H_d_t_i[Hf] = \
      np.clip(L_H_d_t_i[:5][Hf] + Q_star_trs_prt_d_t_i[Hf] - L_normal_uf2room_d_t_i[Hf],
              # NOTE: 送風経路の負荷は部屋の負荷には含めない(24'07)
              # + L_uf2outdoor_d_t_i[Hf] + L_uf2gnd_d_t_i[Hf],
              0, None)
    # 床下→居室全体の項はプラスに働くので負荷としてはマイナス
    return L_star_H_d_t_i, Theta_uf_supply_d_t

def get_L_star_newuf_CS_d_t_i(L_CS_d_t_i, Q_star_trs_prt_d_t_i, region,
                        A_A, A_MR, A_OR, Q, r_A_ufac, underfloor_insulation, Theta_uf_d_t, Theta_ex_d_t,
                        V_dash_supply_d_t_i, L_dash_H_R_d_t, L_dash_CS_R_d_t, Theta_star_HBR_d_t, R_g, di: Injector = None):
    """(9-1)(9-2)(9-3)

    Args:
      L_CS_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの冷房顕熱負荷（MJ/h）
      Q_star_trs_prt_d_t_i: 日付dの時刻tにおける暖冷房区画iの1時間当たりの熱損失を含む負荷バランス時の非居室への熱移動（MJ/h）
      region: 地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      r_A_ufac(float): 当該住戸において、床下空間全体の面積に対する 空調空気を供給する床下空間の面積の比(-)
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      Theta_uf_d_t(ndarray): 床下空間の空気の温度 (℃)
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      V_dash_supply_d_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iのVAV調整前の熱源機の風量（m3/h）
      L_dash_H_R_d_t(ndarray): 標準住戸の負荷補正前の暖房負荷 (MJ/h)
      L_dash_CS_R_d_t(ndarray): 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）
      Theta_star_HBR_d_t: -
      R_g: 地盤またはそれを覆う基礎の表面熱伝達抵抗 ((m2・K)/W)
      di: DIコンテナー

    Returns:
      日付dの時刻tにおける暖冷房区画iの1時間当たりの熱損失を含む負荷バランス時の冷房顕熱負荷

    """
    # 事前条件: 床下空調 新ロジックのみで使用
    assert jjj_consts.change_underfloor_temperature == 床下空調ロジック.変更する.value, \
      "床下空調 新ロジック で実行されることを想定しています"

    jjj_consts.done_binsearch_newufac = True

    # 床下との熱交換による熱負荷の補正
    L_normal_uf2room_d_t_i, L_newuf2room_d_t_i, L_uf2outdoor_d_t_i, L_uf2gnd_d_t_i, Theta_uf_supply_d_t \
      = get_delta_L_star_newuf(
        region, A_A, A_MR, A_OR, Q, r_A_ufac, underfloor_insulation, Theta_uf_d_t, Theta_ex_d_t,
        V_dash_supply_d_t_i, L_dash_H_R_d_t, L_dash_CS_R_d_t, Theta_star_HBR_d_t, R_g, di)

    jjj_consts.done_binsearch_newufac = False
    # NOTE: こちらの調査用ログの出力は省略しています

    H, C, M = dc.get_season_array_d_t(region)
    Cf = np.logical_and(C, L_CS_d_t_i[:5] > 0)

    L_star_CS_d_t_i = np.zeros((5, 24 * 365))
    L_star_CS_d_t_i[Cf] = \
      np.clip(L_CS_d_t_i[:5][Cf] + Q_star_trs_prt_d_t_i[Cf] - L_normal_uf2room_d_t_i[Cf],
              # NOTE: 送風経路の負荷は部屋の負荷には含めない(24'07)
              # + L_uf2outdoor_d_t_i[Cf] + L_uf2gnd_d_t_i[Cf],
              0, None)
    return L_star_CS_d_t_i

@jjj_clone
def get_delta_L_star_newuf(
  region, A_A, A_MR, A_OR, Q, r_A_ufvnt, underfloor_insulation, Theta_uf_d_t, Theta_ex_d_t,
  V_dash_supply_d_t_i, L_dash_H_R_d_t, L_dash_CS_R_d_t, Theta_star_HBR_d_t, R_g, di: Injector = None):
  """床下空調に関する 熱負荷の補正項 冷暖房共通(8)(9)

    Args:
      region: 地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      r_A_ufvnt(float): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      Theta_uf_d_t(ndarray): 床下空間の空気の温度 (℃)
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      V_dash_supply_d_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iのVAV調整前の熱源機の風量（m3/h）
      L_dash_H_R_d_t(ndarray): 標準住戸の負荷補正前の暖房負荷 (MJ/h)
      L_dash_CS_R_d_t(ndarray): 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）
      R_g: 地盤またはそれを覆う基礎の表面熱伝達抵抗 ((m2・K)/W)
      di: DIコンテナー

    Returns:
      日付dの時刻tにおける暖冷房区画iの 1時間当たり 熱交換による熱負荷の補正 [MJ/h]
      L_normal_uf2room_d_t_i: 非床下空調時の床下からの損失分
      L_newuf2room_d_t_i: 床下→居室全体
      L_uf2outdoor_d_t_i: 床下→外気
      L_uf2gnd_d_t_i: 床下→地盤
      Theta_uf_supply_d_t: 温度中和を見込んだ供給温度（℃）

  """
  # 事前条件:
  assert jjj_consts.change_underfloor_temperature == 床下空調ロジック.変更する.value, \
    "床下空調ロジックのみで実行されることを想定"

  # 当該住戸の1時間当たりの換気量 (m3/h) D.3.2 (4)
  # NOTE: 床下のある一階居室(LDK&和室)の給気風量
  V_sa_d_t = np.sum(V_dash_supply_d_t_i[:2, :], axis=0)  # (5,8760) -> (8760, )

  Theta_uf_d_t, _, A_s_ufvnt_i, A_s_ufvnt_A, Theta_g_avg, Theta_dash_g_surf_A_m_d_t, L_uf, H_floor, psi, Phi_A_0, H_star_d_t_i, _, Theta_uf_supply_d_t = \
    dc.calc_Theta(
      region, A_A, A_MR, A_OR, Q,
      r_A_ufvnt, underfloor_insulation,
      Theta_uf_d_t,  # Theta_sa_d_t=
      Theta_ex_d_t,
      V_sa_d_t,  # V_sa_d_t_A=
      '',  # H_OR_C= 機能してない
      L_dash_H_R_d_t, L_dash_CS_R_d_t, R_g, di)
  U_s = dc.get_U_s()  # [W/m2・K]

  # 温度低下を加味した給気温度 ここでは使わないが後で使うために返す

  """熱損失[W] (1)式より各項"""

  # NOTE: L_H_d_t_i, L_CS_d_t_i に含まれている通常(非床下空調)の床下ロス部分(室内→床下→屋外)
  # 下記の補正を追加する前にコチラを引くことでイコールフッティングできます
  L_normal_uf2room_d_t_i = \
    U_s * np.array(A_s_ufvnt_i[:5]).reshape(-1, 1) \
      * (np.abs(Theta_star_HBR_d_t - Theta_ex_d_t) * H_floor).reshape(1, -1) * 3.6 / 1_000  # [MJ/h]
  # 1~5: 1,2階居室

  # 床下 → 床上居室全体()
  # H_floor: 床の温度差係数(-) は通常遮蔽されており(0.7)だが、床下空調時ではスカしているため(1.0)となる値
  assert np.sum(A_s_ufvnt_i) == A_s_ufvnt_A, "一階居室全体"
  L_newuf2room_d_t_i = \
    U_s * np.array(A_s_ufvnt_i[:5]).reshape(-1, 1) \
      * (np.abs(Theta_uf_d_t - Theta_star_HBR_d_t) * 1.0).reshape(1, -1) * 3.6 / 1_000  # [MJ/h]

  # 床下 → 外気
  # [W/m*K]・[m]・[K] → [W] → [MJ/h]
  L_uf2outdoor_d_t = psi * L_uf * np.abs(Theta_ex_d_t - Theta_uf_d_t) * 3.6 / 1_000

  # 床下 → 地盤
  # θ'_g_surf_A_m_d_t: 日付dの時刻tにおける 指数項mの 吸熱応答の項別成分 [℃]
  # θ_g_avg: 地盤の不易層温度 [℃]
  L_uf2gnd_d_t = (A_s_ufvnt_A / R_g) / (1 + Phi_A_0 / R_g) \
    * (Theta_uf_d_t - np.sum(Theta_dash_g_surf_A_m_d_t, axis=1) - Theta_g_avg) * 3.6 / 1_000  # [MJ/h]
  # CHECK: θ'g_surf_A_d_t の値に不一致アリ

  """それぞれをd_t_i化する(面積比で按分)"""

  ratio = np.array(A_s_ufvnt_i) / A_s_ufvnt_A  # shape(12, )
  assert np.isclose(np.sum(A_s_ufvnt_i), A_s_ufvnt_A, rtol=1e-5)
  assert np.isclose(sum(ratio), 1, rtol=1e-5)

  ratio = ratio.reshape(1, -1)
  L_uf2outdoor_d_t_i = ratio.T * L_uf2outdoor_d_t
  L_uf2gnd_d_t_i = ratio.T * L_uf2gnd_d_t

  return L_normal_uf2room_d_t_i, L_newuf2room_d_t_i, L_uf2outdoor_d_t_i[:5], L_uf2gnd_d_t_i[:5], Theta_uf_supply_d_t

@jjj_clone
def calc_Q_hat_hs(
        Q: float,
        A_A: float,
        V_vent_l: float,
        V_vent_g_i: NDArray[Shape["5, 1"], Float64],
        mu_H: float,
        mu_C: float,
        J: float,
        q_gen: float,
        n_p: float,
        q_p_H: float,
        q_p_CS: float,
        q_p_CL: float,
        X_ex: float,
        w_gen: float,
        Theta_ex: float,
        L_wtr: float,
        HCM: JJJ_HCM  # regionの代替
        ) -> float:
    """単時点版 (40-1a)(40-1b)(40-2a)(40-2b)(40-2c)(40-3)

    Args:
        Q: 当該住戸の熱損失係数 [W/(m2・K)]
        A_A: 床面積の合計 [m2]
        V_vent_l: 局所換気量 [m3/h]
        V_vent_g_i: 暖冷房区画iの全般換気量 [m3/h]
        mu_H: 当該住戸の暖房期の日射取得係数 [(W/m2)/(W/m2)]
        mu_C: 当該住戸の冷房期の日射取得係数 [(W/m2)/(W/m2)]
        J: 水平面全天日射量 [W/m2]
        q_gen: 内部発熱 [W]
        n_p: 在室人数 [人]
        q_p_H: 暖房期における人体からの1人当たりの顕熱発熱量 [W/人]
        q_p_CS: 冷房期における人体からの1人当たりの顕熱発熱量 [W/人]
        q_p_CL: 冷房期における人体からの1人当たりの潜熱発熱量 [W/人]
        X_ex: 外気の絶対湿度 [kg/kg(DA)]
        w_gen: 内部発湿量 [kg/h]
        Theta_ex: 外気温度（℃）
        L_wtr: 水の蒸発潜熱 [kJ/kg]
        HCM: 季節区分

    Returns:
        (時点)１時間当たりの熱源機の風量を計算するための熱源機の暖房出力 [MJ/h]
    """
    c_p_air = dc.get_c_p_air()
    rho_air = dc.get_rho_air()
    Theta_set_H = dc.get_Theta_set_H()
    Theta_set_C = dc.get_Theta_set_C()
    X_set_C = dc.get_X_set_C()

    match HCM:
        case JJJ_HCM.H:
            # (40-1b)
            Q_hat_hs_H = (
                (Q - 0.35 * 0.5 * 2.4) * A_A  # 外皮
                + (c_p_air * rho_air * (V_vent_l + np.sum(V_vent_g_i))) / 3600  # 換気
                ) * (Theta_set_H - Theta_ex)
            Q_hat_hs_H -= mu_H * A_A * J  # 日射
            Q_hat_hs_H -= q_gen  # 内部発熱
            Q_hat_hs_H -= n_p * q_p_H  # 人体発熱
            # (40-1a)
            return max(Q_hat_hs_H * 3600 * 1e-6, 0)

        case JJJ_HCM.C:
            # (40-2b)
            Q_hat_hs_CS = (
                ((Q - 0.35 * 0.5 * 2.4) * A_A
                + (c_p_air * rho_air * (V_vent_l + np.sum(V_vent_g_i))) / 3600
                ) * (Theta_ex - Theta_set_C) \
                + mu_C * A_A * J \
                + q_gen \
                + n_p * q_p_CS) * 3600 * 1e-6
            # (40-2c)
            Q_hat_hs_CL = (
                (rho_air * (V_vent_l + np.sum(V_vent_g_i)) * (X_ex - X_set_C) * 10^3 + w_gen) * L_wtr \
                + n_p * q_p_CL * 3600) * 1e-6
            # (40-2a)
            return (max(Q_hat_hs_CS, 0) + max(Q_hat_hs_CL, 0))

        case JJJ_HCM.M:
            # (40-3)
            return 0

        case _:
            raise ValueError("Invalid season flag")
