import math
import pandas as pd

from jjjexperiment.denchu_1 import *

from pyhees.section11_1 import \
    get_Theta_ex, get_X_ex, load_climate

from jjjexperiment.logger import LimitedLoggerAdapter as _logger  # デバッグ用ロガー

def simu_R(a2, a1, a0):
    """ 二次関数 R(q) を得る """
    return lambda x: a2*x**2 + a1*x + a0

def simu_P(q: float, COP: float) -> float:
    return q / COP

def simu_COP_C(q: float, Pc: float, R: float, M_ein: float, M_cin: float, cdtn: Condition) -> float:
    """Args:
        q [kW]:
        Pc [kW]:
        R [kW]:
        M_ein, M_cin [kgDA/s]:
        cdtn:
    """

    """ 推計モデルと実使用条件から COPを推計する """
    def fix_T_evp(q, M_ein, cdtn: Condition):
        """ q [kW] """
        Ca = get_Ca(cdtn.X_ein / 1000)
        T_evp = cdtn.T_ein - q / ((1-BF) * M_ein * Ca)  #★
        return T_evp

    def simu_T_cnd(q, P, M_cin, cdtn: Condition):
        """ q, P [kW] """
        Ca = get_Ca(cdtn.X_cin / 1000)
        T_cnd = cdtn.T_cin + (q+P) / ((1-BF) * M_cin * Ca)  #★
        return T_cnd

    def recalc_COP(q, R, Pc, T_evp, T_cnd) -> float:
        left = R * (T_evp + 273.15) / (T_cnd - T_evp)  #★
        return left * q / (q + Pc * left)

    if q==0: return 0

    # FIXME: 多数のCOPが100をゆうに超えた値で収束する問題がある
    T_evp = fix_T_evp(q, M_ein, cdtn)  #★
    COP = 5; loop_cnt = 0  # 初期値はなんでも可、収束ロジックは論文のとおり
    while loop_cnt <= 100:  # FIXME: 計算回数に上限を設定しています
        P = simu_P(q, COP)
        T_cnd = simu_T_cnd(q, P, M_cin, cdtn)
        test_COP = recalc_COP(q, R, Pc, T_evp, T_cnd)

        # FIXME: 精度コントロール
        if math.isclose(test_COP, COP, abs_tol=1e-3):
            break
        else:
            COP = test_COP
            loop_cnt += 1
    return COP

def simu_COP_H(q: float, Pc: float, R: float, M_ein: float, M_cin: float, cdtn: Condition) -> float:
    """Args:
        q [kW]:
        Pc [kW]:
        R [kW]:
        M_ein, M_cin [kgDA/s]:
        cdtn:
    """

    """ 推計モデルと実使用条件から COPを推計する """
    def fix_T_cnd(q, M_cin, cdtn: Condition):
        """ q [kW] """
        Ca = get_Ca(cdtn.X_cin / 1000)
        T_cnd = cdtn.T_cin + q / ((1-BF) * M_cin * Ca)  #★
        return T_cnd

    def simu_T_evp(q, P, M_ein, cdtn: Condition):
        """ q, P [kW] """
        Ca = get_Ca(cdtn.X_ein / 1000)
        T_evp = cdtn.T_ein - (q-P) / ((1-BF) * M_ein * Ca)  #★
        return T_evp

    def recalc_COP(q, R, Pc, T_evp, T_cnd) -> float:
        left = R * (T_cnd + 273.15) / (T_cnd - T_evp)  #★
        return left * q / (q + Pc * left)

    if q==0: return 0

    T_cnd = fix_T_cnd(q, M_cin, cdtn)  #★
    COP = 5; loop_cnt = 0  # 初期値はなんでも可、収束ロジックは論文のとおり
    while loop_cnt <= 100:  # FIXME: 計算回数に上限を設定しています
        P = simu_P(q, COP)
        T_evp = simu_T_evp(q, P, M_ein, cdtn)
        test_COP = recalc_COP(q, R, Pc, T_evp, T_cnd)

        # FIXME: 精度コントロール
        if math.isclose(test_COP, COP, abs_tol=1e-2):
            break
        else:
            COP = test_COP
            loop_cnt += 1
    return COP

def calc_COP_C_d_t(q_d_t, P_rac_fan_rtd, R,
                    V_rac_inner_d_t, V_rac_outer_d_t, region,
                    Theta_real_inner, RH_real_inner, climateFile):
    """
    Args:
        q_d_t [kW] \n
        P_rac_fan_rtd [kW] \n
        R: 関数オブジェクト R(q) \n
        V_rac_inner_d_t [m3/h] \n
        V_rac_outer_d_t [m3/h] \n
        Theta_real_inner [℃]: 室内温度設定 \n
        RH_real_inner [%]: 室内相対湿度設定 \n
        climateFile: 気象データファイル \n
    """
    """ 外気条件(時系列変化) 6.1 (5) 同様 """

    if climateFile == '-':
        climate = load_climate(region)
    else:
        climate = pd.read_csv(climateFile, nrows=24 * 365, encoding="SHIFT-JIS")
    Theta_ex = get_Theta_ex(climate)
    X_ex = get_X_ex(climate)

    """ 室内条件(固定?) """

    # TODO: 入力させてよいのか？すでにあるか？
    X_inner = absolute_humid(RH_real_inner, Theta_real_inner)  # 10前後でOK

    COP_d_t: np.ndarray = np.zeros(24*365)
    for i in range(len(Theta_ex)):
        cdtn = Condition(Theta_ex[i], Theta_real_inner, X_ex[i], X_inner)

        M_ein = m3ph_to_kgDAps(V_rac_inner_d_t[i], Theta_real_inner)           # 室内
        M_cin = m3ph_to_kgDAps(V_rac_outer_d_t[i], Theta_ex[i])  # 室外

        cop = simu_COP_C(q_d_t[i], P_rac_fan_rtd, R(q_d_t[i]), M_ein, M_cin, cdtn)
        COP_d_t[i] = cop

    return COP_d_t

def calc_COP_H_d_t(q_d_t, P_rac_fan_rtd, R,
                   V_rac_inner_d_t, V_rac_outer_d_t, region,
                   Theta_real_inner, RH_real_inner, climateFile):
    """
    Args:
        q_d_t: [kW]\n
        P_rac_fan_rtd: [kW]\n
        R: 関数オブジェクト R(q)\n
        V_hs_d_t: [m3/h]\n
        Theta_real_inner [℃]: 室内温度設定 \n
        RH_real_inner [%]: 室内相対湿度設定 \n
    """
    """ 外気条件(時系列変化) 6.1 (5) 同様 """

    if climateFile == '-':
        climate = load_climate(region)
    else:
        climate = pd.read_csv(climateFile, nrows=24 * 365, encoding="SHIFT-JIS")
    Theta_ex = get_Theta_ex(climate)
    X_ex = get_X_ex(climate)

    _logger.NDdebug(f"Theta_ex", Theta_ex)
    _logger.NDdebug(f"X_ex", X_ex)

    """ 室内条件(固定?) """

    X_inner = absolute_humid(RH_real_inner, Theta_real_inner)  # 10前後でOK

    COP_d_t: np.ndarray = np.zeros(24*365)
    for i in range(len(Theta_ex)):
        cdtn = Condition(Theta_ex[i], Theta_real_inner, X_ex[i], X_inner)

        M_ein = m3ph_to_kgDAps(V_rac_outer_d_t[i], Theta_ex[i])  # 室外
        M_cin = m3ph_to_kgDAps(V_rac_inner_d_t[i], Theta_real_inner)           # 室内

        cop = simu_COP_H(q_d_t[i], P_rac_fan_rtd, R(q_d_t[i]), M_ein, M_cin, cdtn)
        COP_d_t[i] = cop

    return COP_d_t  # 10いかないはず
