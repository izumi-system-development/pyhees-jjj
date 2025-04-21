import numpy as np

import pyhees.section3_1_e as algo
import pyhees.section4_2 as dc
# JJJ
from jjjexperiment.app_config import *
from jjjexperiment.di_container import *
from jjjexperiment.common import *
from jjjexperiment.options import *


def get_r_A_uf_i() -> Array12x1:
    """暖冷房区画iの床面積のうち床下空間に接する床面積の割合 (-)
    """
    r_A_uf_i = np.array([
            algo.get_r_A_uf_i(i) for i in range(1, 13)
        ]).reshape(-1, 1)
    assert r_A_uf_i.shape == (12, 1)
    return r_A_uf_i


def get_A_s_ufac_i(
        A_A: float,
        A_MR: float,
        A_OR: float
    ) -> tuple[Array12x1, float]:
    """
    Returns:
        tuple(Array12x1, float):
            - A_s_ufac_i: 暖冷房区画iの床下空調有効面積[m2]
            - r_A_s_ufac: 面積全体における床下空調部分の床面積の比率[-]
    """
    r_A_ufac = 1.0  # 床下空調利用時の有効率
    A_s_ufac_i \
        = np.array([
            # 床面積 * 床下空調部分割合 * 有効率
            algo.calc_A_s_ufvnt_i(i, r_A_ufac, A_A, A_MR, A_OR)
            for i in range(1, 13)
        ]).reshape(-1, 1)
    assert np.shape(A_s_ufac_i) == (12, 1)

    # 面積全体における 床下空調部分の床面積の割合
    r_A_s_ufac = np.sum(A_s_ufac_i) / A_A

    return A_s_ufac_i, r_A_s_ufac

# 計算方法はいくつかあるので使い分けを確認する
# ex. pyhees.section4_2.calc_Theta_uf
# ex. pyhees.section4_2.calc_Theta_uf_d_t_2023


def calc_Theta_uf(
        L_H_flr1st: float,
        A_s_ufvnt: float,
        U_s_vert: float,
        Theta_in: float,
        Theta_ex: float,
        V_flr1st: float,
        ) -> float:
    """床下空間の温度 (40-4) 単時点

    Args:
        L_H_flr1st: 一階部分の1時間当たりの暖房負荷 [MJ/h]
        A_s_ufvnt: 空気を供給する床下空間に接する床の面積 [m2]
        U_s_vert: 床の熱貫流率 [W/m2K]
        Theta_in: 室温 [℃]
        Theta_ex: 外気温度 [℃]
        V_flr1st: 第1床面積 [m2]

    Returns:
        床下空間の温度 [℃]
    """
    ro_air = dc.get_ro_air()    # 空気密度 [kg/m3]
    c_p_air = algo.get_c_p_air()  # 空気の比熱 [kJ/kgK]

    H_floor = 0.7  # 床の温度差係数(-) 損失として

    b = ro_air * c_p_air * V_flr1st + U_s_vert * A_s_ufvnt * 3.6
    a1 = L_H_flr1st * 1e+3
    a2 = U_s_vert * A_s_ufvnt * np.abs(Theta_in - Theta_ex) * H_floor * 3.6

    Theta_uf = (a1 - a2 + Theta_in * b) / b
    return Theta_uf


# vectorizeできなのいのでhstack-broadcastで対応 (A_s_ufac_iが強制でfloatになるため)
def calc_delta_L_room2uf_i(
        U_s_vert: float,
        A_s_ufac_i: Array5x1,
        delta_Theta: float
    ) -> Array5x1:
    """床下空間から居室全体への熱損失 [MJ/h]

    Args:
        U_s_vert: 床の熱貫流率 [W/m2・K]

    """
    assert A_s_ufac_i.ndim == 2

    H_floor = 0.7  # 床下空調でなく意図しない熱移動の分なので通常の遮蔽係数(0.7)となる
    delta_L_uf2room =  U_s_vert * A_s_ufac_i * np.abs(delta_Theta) * H_floor \
        * 3.6 / 1000  # [W] -> [MJ/h]
    # NOTE: L_H_d_t_i, L_CS_d_t_i に含まれている通常(非床下空調)の床下ロス部分(室内→床下→屋外)
    # 下記の補正を追加する前にコチラを引くことでイコールフッティングできます
    assert delta_L_uf2room.ndim == 2
    return delta_L_uf2room  # TODO: i=1~5でトリムするか検討


def calc_delta_L_uf2outdoor(
        phi: float,
        L_uf: float,
        delta_Theta: float
    ) -> float:
    """床下空間から外気への熱損失 [MJ/h]
    Args:
        phi: 土間床等の外気に接する床の熱貫流率 [W/m2K]
        L_uf: 土間床等の外気に接する床の周辺部の長さ [m]
        delta_Theta: 床下空間と外気の温度差 [℃]
    """
    return phi * L_uf * np.abs(delta_Theta) * 3.6 / 1000  # [W] -> [MJ/h]


def calc_delta_L_uf2gnd(
        q_hs_rtd_H: float,
        q_hs_rtd_C: float,
        A_s_ufvnt_A: float,
        R_g: float,
        Phi_A_0: float,
        Theta_uf: float,
        sum_Theta_dash_g_surf_A_m: float,
        Theta_g_avg: float
    ) -> float:
    """床下空間から地盤への熱損失 [MJ/h]
    Args:
        A_s_ufvnt_A: 空気を供給する床下空間に接する床の面積 [m2]
        R_g: 地盤またはそれを覆う基礎の表面熱伝達抵抗 [m2・K/W]
        Phi_A_0: 吸熱応答係数の初項
        Theta_uf: 床下空間の温度 [℃]
        sum_Theta_dash_g_surf_A_m: 指数項mの吸熱応答の項別成分の合計 [℃]
        Theta_g_avg: 地盤の不易層温度 [℃]
    """
    # CHECK: θ'g_surf_A_d_t の値に不一致アリ
    delta_Theta = Theta_uf - sum_Theta_dash_g_surf_A_m - Theta_g_avg

    # 暖冷房期 判別
    match(q_hs_rtd_H, q_hs_rtd_C):
        case (None, None):
            raise Exception("q_hs_rtd_H, q_hs_rtd_C はどちらかのみを前提")
        case (_, None):  # 暖房期
            delta_Theta = 1 * delta_Theta
        case (None, _):  # 冷房期
            delta_Theta = -1 * delta_Theta
        case (_, _):
            raise Exception("q_hs_rtd_H, q_hs_rtd_C はどちらかのみを前提")

    return (A_s_ufvnt_A / R_g) / (1 + Phi_A_0 / R_g)  \
        * delta_Theta * 3.6 / 1000  # [W] -> [MJ/h]

# もう使用しないことにした、これで問題ないならメソッドごと消す
def get_delta_L_star_newuf(
        region, A_A, A_MR, A_OR, Q, r_A_ufac, U_s_vert, underfloor_insulation, Theta_uf_d_t, Theta_ex_d_t,
        V_dash_supply_d_t_i, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i, Theta_star_HBR_d_t, R_g, di: Injector = None):
    """床下空調に関する 熱負荷の補正項 冷暖房共通(8)(9)

      Args:
        region: 地域区分
        A_A(float): 床面積の合計 (m2)
        A_MR(float): 主たる居室の床面積 (m2)
        A_OR(float): その他の居室の床面積 (m2)
        Q(float): 当該住戸の熱損失係数 (W/m2K)
        r_A_ufac(float): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
        U_s_vert: 床の熱貫流率 [W/m2・K]
        underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
        Theta_uf_d_t(ndarray): 床下空間の空気の温度 (℃)
        Theta_ex_d_t(ndarray): 外気温度 (℃)
        V_dash_supply_d_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iのVAV調整前の熱源機の風量（m3/h）
        L_dash_H_R_d_t_i(ndarray): 標準住戸の負荷補正前の暖房負荷 (MJ/h)
        L_dash_CS_R_d_t_i(ndarray): 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）
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
    assert injector.get(AppConfig).new_ufac_flg == 床下空調ロジック.変更する.value,  \
        "床下空調ロジックのみで実行されることを想定"

    # 当該住戸の1時間当たりの換気量 (m3/h) D.3.2 (4)
    # NOTE: 床下のある一階居室(LDK&和室)の給気風量
    # (5,8760) -> (8760, )
    V_sa_d_t = np.sum(V_dash_supply_d_t_i[:2, :], axis=0)

    Theta_uf_d_t, _, A_s_ufvnt_i, A_s_ufvnt_A, Theta_g_avg, Theta_dash_g_surf_A_m_d_t, L_uf, H_floor, psi, Phi_A_0, H_star_d_t_i, _, Theta_uf_supply_d_t = \
        dc.calc_Theta(
            region, A_A, A_MR, A_OR, Q,
            r_A_ufac, underfloor_insulation,
            Theta_uf_d_t,  # Theta_sa_d_t=
            Theta_ex_d_t,
            V_sa_d_t,  # V_sa_d_t_A=
            '',  # H_OR_C= 機能してない
            L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i, di)

    # 温度低下を加味した給気温度 ここでは使わないが後で使うために返す

    """熱損失[W] (1)式より各項"""

    delta_Theta_room2uf = np.abs(Theta_star_HBR_d_t - Theta_ex_d_t)
    # 床下 → 床上居室全体()
    assert A_s_ufvnt_i.ndim == 1
    delta_L_room2uf_d_t_i  \
        = np.hstack([
            calc_delta_L_room2uf_i(
                U_s_vert, A_s_ufvnt_i.reshape(-1,1),
                delta_Theta_room2uf[tt])
            for tt in range(24*365)
        ])
    assert delta_L_room2uf_d_t_i.ndim == 2

    # 床下 → 外気
    delta_L_uf2outdoor_d_t = np.vectorize(calc_delta_L_uf2outdoor)
    delta_L_uf2outdoor_d_t \
        = delta_L_uf2outdoor_d_t(psi, L_uf, Theta_uf_d_t - Theta_ex_d_t)
    assert delta_L_uf2outdoor_d_t.ndim == 1

    # 床下 → 地盤
    # 他へ移動しました

    """それぞれをd_t_i化する(面積比で按分)"""

    ratio = np.array(A_s_ufvnt_i) / A_s_ufvnt_A  # shape(12, )
    assert np.isclose(np.sum(A_s_ufvnt_i), A_s_ufvnt_A, rtol=1e-5)
    assert np.isclose(sum(ratio), 1, rtol=1e-5)

    ratio = ratio.reshape(1, -1)  # -1,1 に合わせるか
    delta_L_uf2outdoor_d_t_i = ratio.T * delta_L_uf2outdoor_d_t

    return delta_L_room2uf_d_t_i, delta_L_uf2outdoor_d_t_i[:5], Theta_uf_supply_d_t
