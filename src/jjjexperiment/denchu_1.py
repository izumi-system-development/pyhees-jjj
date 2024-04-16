import typing
from math import exp, log
import numpy as np
import pandas as pd

from jjjexperiment.logger import LimitedLoggerAdapter as _logger, log_res

ATM_AIR_PRESSURE = 1013.25
""" 大気圧[hPa] """
BF = 0.2  # NOTE: 論文内では0.2に固定
""" Bypass-Factor """

class Spec:
    """ 機器特性(メーカー公表値)をまとめるクラス
    """
    def __init__(self,
                P_rac_min, P_rac_rtd, P_rac_max,
                q_rac_min, q_rac_rtd, q_rac_max,
                V_inner, V_outer, name=""):
        self._name = name
        self._p_rac_min, self._p_rac_rtd, self._p_rac_max = P_rac_min, P_rac_rtd, P_rac_max
        self._q_rac_min, self._q_rac_rtd, self._q_rac_max = q_rac_min, q_rac_rtd, q_rac_max
        self._V_inner, self._V_outer = V_inner, V_outer

    @property
    def name(self):
        """ 機器名 """; return self._name
    @property
    def P_rac_min(self):
        """ JIS条件での消費電力(最小)[W] """; return self._p_rac_min
    @property
    def P_rac_rtd(self):
        """ JIS条件での消費電力(定格)[W] """; return self._p_rac_rtd
    @property
    def P_rac_max(self):
        """ JIS条件での消費電力(最大)[W] """; return self._p_rac_max

    # NOTE: 室内から除去するエネルギー = 冷房能力 (論文より)
    @property
    def q_rac_min(self):
        """ JIS条件での熱処理能力(最小)[kW] """; return self._q_rac_min
    @property
    def q_rac_rtd(self):
        """ JIS条件での熱処理能力(定格)[kW] """; return self._q_rac_rtd
    @property
    def q_rac_max(self):
        """ JIS条件での熱処理能力(最大)[kW] """; return self._q_rac_max

    # NOTE: evp,cnd は冷暖で逆になるため室内機・室外機の識別子にはならない
    # よって inner, outer で表現する
    @property
    def V_inner(self):
        """ 室内機の吸込み空気量[m3/min] """; return self._V_inner
    @property
    def V_outer(self):
        """ 室外機の吸込み空気量[m3/min] """; return self._V_outer

    def outputDataFrame(self, data_frame):
        """csv出力用のデータフレーム"""
        data_frame.loc[Spec.P_rac_min.__doc__] = [self.P_rac_min]
        data_frame.loc[Spec.P_rac_rtd.__doc__] = [self.P_rac_rtd]
        data_frame.loc[Spec.P_rac_max.__doc__] = [self.P_rac_max]
        data_frame.loc[Spec.q_rac_min.__doc__] = [self.q_rac_min]
        data_frame.loc[Spec.q_rac_rtd.__doc__] = [self.q_rac_rtd]
        data_frame.loc[Spec.q_rac_max.__doc__] = [self.q_rac_max]
        data_frame.loc[Spec.V_inner.__doc__] = [self.V_inner]
        data_frame.loc[Spec.V_outer.__doc__] = [self.V_outer]
        return data_frame

class Condition():
    """ エアコンの使用条件をまとめるクラス
    """
    def __init__(self, T_ein, T_cin, X_ein, X_cin):
        self._T_ein, self._T_cin = T_ein, T_cin
        self._X_ein, self._X_cin = X_ein, X_cin

    # NOTE: ein, cin が部屋の内・外かどうかは冷房・暖房によって変わる
    @property
    def T_ein(self):
        """ 蒸発器と接する空気の温度[℃] """; return self._T_ein
    @property
    def T_cin(self):
        """ 凝集器と接する空気の温度[℃] """; return self._T_cin

    @property
    def X_ein(self):
        """ 蒸発器と接する空気の絶対湿度[g/kgDA] """; return self._X_ein
    @property
    def X_cin(self):
        """ 蒸発器と接する空気の絶対湿度[g/kgDA] """; return self._X_cin

    def outputDataFrame(self, data_frame):
        """csv出力用のデータフレーム"""
        data_frame.loc[Condition.T_ein.__doc__] = [self.T_ein]
        data_frame.loc[Condition.T_cin.__doc__] = [self.T_cin]
        data_frame.loc[Condition.X_ein.__doc__] = [self.X_ein]
        data_frame.loc[Condition.X_cin.__doc__] = [self.X_cin]
        return data_frame

def get_DataFrame_denchu_modeling_consts(
        spec: Spec, cdtn: Condition,
        R2: float, R1: float, R0: float,
        T_real: float, RH_real: float, Pc: float) -> pd.DataFrame:
        """ 電柱研モデル化の定数確認用データフレーム
            Args:
                Pc: ファン等消費電力Pc [W]
        """
        df = pd.DataFrame(index=['電中研モデリング定数'], columns=['値'])
        df = spec.outputDataFrame(df)
        df = cdtn.outputDataFrame(df)
        df = df._append(
            pd.DataFrame([[R2], [R1], [R0]], columns=df.columns, index=['R2', 'R1', 'R0'])
        )
        df.loc['ファン等消費電力Pc [W]'] = [Pc]
        df.loc['実際の使用状況におけるエアコン吸込み空気の 温度 [℃]'] = [T_real]
        df.loc['実際の使用状況におけるエアコン吸込み空気の 相対温度 [%]'] = [RH_real]
        return df

def dry_air_density(temperature: float) -> float:
    """ 気温[℃]毎の乾燥空気の密度[kg/m3] """
    return ATM_AIR_PRESSURE / (2.87 * (temperature + 273.15))

def absolute_humid(rh: float, t: float):
    """ 気温[℃]毎の相対湿度[%]から、重量絶対湿度[g/kgDA]へ変換
    """
    # 数式参考: https://www.2x6satoru.com/article/ab-humidity.html
    e = 6.1078 * 10 ** (7.5 * t / (t + 237.3)) * (rh / 100)
    return 0.622 * e / (ATM_AIR_PRESSURE - e) * 1000

def calc_Pa_wexler(Td: float) -> float:
    """ Td[℃]から ウェクスラー・ハイランド式によって飽和水蒸気量[Pa]を計算 """
    tmp = Td + 273.15
    Pws = exp(-5800.2206 / tmp + 1.3914993 + tmp * (-0.048640239 + tmp * (0.000041764768 - 0.000000014452093 * tmp)) + 6.5459673 * log(tmp))
    return Pws

def Pa_to_gkgDA(hpa: float) -> float:
    """ 水蒸気圧[hPa]から絶対湿度[g/kg(DA)]に変換 """
    return 622 * hpa / (ATM_AIR_PRESSURE - hpa)

def m3ph_to_kgDAps(m3ph: float, temperature: float) -> float:
    """ 空気の流量を 体積流量[m3/h] -> 質量流量[kg(DA)/s]に変換 """
    rho = dry_air_density(temperature)
    return rho * m3ph / 3600

def is_over_saturated(Td: float, X: float) -> bool:
    """ その温度[℃]の空気が保持できる絶対湿度[g/kg(DA)]を超えているか調べる """
    saturated_steam_pressure = 0.01 * calc_Pa_wexler(Td)
    x_limit = Pa_to_gkgDA(saturated_steam_pressure)
    return x_limit < X

def avoid_over_saturated(Td: float, X: float) -> float:
    """ 空気の温度[℃]から飽和[g/kg(DA)]をチェックし等エンタルピー線に沿って温度[℃]が上げて飽和状態に留める
    既知: 相対湿度(100%), 比エンタルピー -> 目的: 乾球温度
    """
    def specific_enthalpy(Td: float, X: float) -> float:
        """ 乾球温度Td[℃] & 絶対湿度[kg/kg(DA)] -> 比エンタルピ[kJ/kg(DA)] """
        return 1.006 * Td + (1.86 * Td + 2501) * X

    ent = specific_enthalpy(Td, 0.001 * X)  # 比エンタルピーを求め、等エンタルピーに沿って

    # NOTE: 二分探索(binary-search)による実装
    Td_end = 50  # NOTE: 探索の終点
    tmps = [0.001 * i for i in (range(int(Td)*1000, Td_end*1000))]  # NOTE: 探索の精度

    left = 0
    n = len(tmps); right = n-1

    while left <= right:
        center = (left + right) // 2
        Td_check = tmps[center]  # 乾球温度の仮定値

        # 等エンタルピー線上の絶対湿度
        # 参考: https://www.techno-ryowa.co.jp/rrlab/note.html
        X = (ent - 1.006 * Td_check) / (1.86 * Td_check + 2501)

        # その乾球温度における飽和時の絶対湿度
        X_limit = 0.001 * absolute_humid(100, Td_check)  # kg/kg(DA)

        if X_limit < X:
            left = center + 1
        else:
            right = center - 1

    return tmps[left - 1]

def get_Ca(humid_abs: float):
    """ 重量絶対湿度[kg/kg(DA)]から湿り空気の比熱[kJ/kg(DA)*K] を取得
    """
    # 数式参考: https://www.jstage.jst.go.jp/article/jsam1937/37/4/37_4_694/_pdf
    C_g = 1.005
    C_v = 1.8695 * humid_abs  # NOTE: 様々な数字が見られる(1.884...etc)
    return C_g + C_v  # NOTE: 乾き空気の比熱+水蒸気の比熱

@log_res(['T_evp_C', 'T_cnd_C'])
def calc_reibai_phase_T_C(q: float, P: float, spec: Spec, condi: Condition)-> typing.Tuple[float, float]:
    """ q, P [kW]で統一
    """
    M_evp = (1-BF) * m3ph_to_kgDAps(spec.V_inner * 60, condi.T_ein)
    Ca_ein = get_Ca(condi.X_ein / 1000)  # [kJ/(kgDA*K)]
    T_evp = condi.T_ein - q / (M_evp*Ca_ein)

    # 水蒸気保持できなくなった場合
    if is_over_saturated(T_evp, condi.X_ein):
        T_evp = avoid_over_saturated(T_evp, condi.X_ein)

    M_cnd = (1-BF) * m3ph_to_kgDAps(spec.V_outer * 60, condi.T_cin)
    Ca_cin = get_Ca(condi.X_cin / 1000)  # [kJ/(kgDA*K)]
    T_cnd = condi.T_cin + (q+P) / (M_cnd*Ca_cin)

    return T_evp, T_cnd  # 冷媒 蒸発/凝縮 温度[℃]

@log_res(['T_evp_H', 'T_cnd_H'])
def calc_reibai_phase_T_H(q: float, P: float, spec: Spec, condi: Condition)-> typing.Tuple[float, float]:
    """ q, P [kW]で統一
    """
    M_evp = (1-BF) * m3ph_to_kgDAps(spec.V_outer * 60, condi.T_ein)
    Ca_ein = get_Ca(condi.X_ein / 1000)  # [kJ/(kgDA*K)]
    T_evp = condi.T_ein - (q-P) / (M_evp*Ca_ein)

    # 水蒸気保持できなくなった場合
    if is_over_saturated(T_evp, condi.X_ein):
        T_evp = avoid_over_saturated(T_evp, condi.X_ein)

    M_cnd = (1-BF) * m3ph_to_kgDAps(spec.V_inner * 60, condi.T_cin)
    Ca_cin = get_Ca(condi.X_cin / 1000)  # [kJ/(kgDA*K)]
    T_cnd = condi.T_cin + q / (M_cnd*Ca_cin)

    return T_evp, T_cnd  # 冷媒 蒸発/凝縮 温度[℃]

def solve_mtx(A: np.matrix, Y: np.matrix) -> typing.Tuple[float, float]:
    mtx_ans = np.linalg.inv(A) * Y  # shape(2, 1)
    return (mtx_ans[0, 0], mtx_ans[1, 0])

def calc_R_and_Pc_C(spec: Spec, condi: Condition) -> typing.Tuple[float, float, float, float]:
    """ 成績係数比Rの近似式の係数とファン等消費電力Pc[kW]
    """
    def coeffs_for_simultaneous_C(label: str, q:float, P:float, spec: Spec, condi: Condition) -> typing.Tuple[float, float, float]:
        """ q, P [kW]で統一 """
        T_evp, T_cnd = calc_reibai_phase_T_C(q, P, spec, condi)
        A = (T_cnd - T_evp) / (T_evp + 273.15)  # 冷房と異なる
        B = 1 / q
        COP = q / P; Y = 1 / COP
        return A, B, Y  # A・R' + B・Pc = Y (R'=1/R) の形にする

    @log_res(['R_minrtd_C', 'Pc_C'])
    def R_minrtd_C(spec: Spec, condi: Condition) -> typing.Tuple[float, float]:
        A1, B1, Y1 = coeffs_for_simultaneous_C('min_C', spec.q_rac_min, 0.001*spec.P_rac_min, spec, condi)
        A2, B2, Y2 = coeffs_for_simultaneous_C('rtd_C', spec.q_rac_rtd, 0.001*spec.P_rac_rtd, spec, condi)
        mtx_A, mtx_Y = np.matrix([[A1, B1], [A2, B2]]), np.matrix([[Y1], [Y2]])
        R_minrtd_dash, Pc = solve_mtx(mtx_A, mtx_Y)
        R_minrtd = 1 / R_minrtd_dash  # NOTE: 最小・定格時のR同一
        return R_minrtd, Pc

    R_minrtd, Pc = R_minrtd_C(spec, condi)

    def R_max_C(Pc, q, P, spec: Spec, condi: Condition) -> float:
        """ Pc, q, P [kW]で統一 """
        T_evp_max, T_cnd_max = calc_reibai_phase_T_C(q, P, spec, condi)
        COP = q / P
        right = COP * q / (q - COP*Pc)  # (7)式右辺
        left = (T_evp_max + 273.15) / (T_cnd_max - T_evp_max)  # (7)式左辺(係数部)
        return right / left

    # NOTE: 論文より最大時のRのみ別に計算する
    R_max = R_max_C(Pc, spec.q_rac_max, 0.001*spec.P_rac_max, spec, condi)

    Qs = np.array([spec.q_rac_min, spec.q_rac_rtd, spec.q_rac_max])
    Rs = np.array([R_minrtd, R_minrtd, R_max])
    coeffs = np.polyfit(Qs, Rs, 2)  # 二次式に近似し係数を取得

    R_poly_a2 = coeffs[0]
    R_poly_a1 = coeffs[1]
    R_poly_a0 = coeffs[2]
    _logger.info(f"a2: {R_poly_a2}\na1: {R_poly_a1}\na0: {R_poly_a0}")
    return R_poly_a2, R_poly_a1, R_poly_a0, Pc

def calc_R_and_Pc_H(spec: Spec, condi: Condition) -> typing.Tuple[float, float, float, float]:
    """ 成績係数比Rの近似式の係数とファン等消費電力Pc[kW]
    """
    def coeffs_for_simultaneous_H(label: str, q:float, P:float, spec: Spec, condi: Condition) -> typing.Tuple[float, float, float]:
        """ q, P [kW]で統一 """
        T_evp, T_cnd = calc_reibai_phase_T_H(q, P, spec, condi)
        A = (T_cnd - T_evp) / (T_cnd + 273.15)  # 冷房と異なる
        B = 1 / q
        COP = q / P; Y = 1 / COP
        return A, B, Y  # A・R' + B・Pc = Y (R'=1/R) の形にする

    @log_res(['R_minrtd_H', 'Pc_H[kW]'])
    def R_minrtd_H(spec: Spec, condi: Condition) -> typing.Tuple[float, float]:
        A1, B1, Y1 = coeffs_for_simultaneous_H('min_H', spec.q_rac_min, 0.001*spec.P_rac_min, spec, condi)
        A2, B2, Y2 = coeffs_for_simultaneous_H('rtd_H', spec.q_rac_rtd, 0.001*spec.P_rac_rtd, spec, condi)
        mtx_A, mtx_Y = np.matrix([[A1, B1], [A2, B2]]), np.matrix([[Y1], [Y2]])
        R_minrtd_dash, Pc = solve_mtx(mtx_A, mtx_Y)
        R_minrtd = 1 / R_minrtd_dash  # NOTE: 最小・定格時のR同一
        return R_minrtd, Pc

    R_minrtd, Pc = R_minrtd_H(spec, condi)

    def R_max_H(Pc, q, P, spec: Spec, condi: Condition) -> float:
        """ Pc, q, P [kW]で統一 """
        T_evp_max, T_cnd_max = calc_reibai_phase_T_H(q, P, spec, condi)
        COP = q / P
        right = COP * q / (q - COP*Pc)  # (7)式右辺
        left = (T_cnd_max + 273.15) / (T_cnd_max - T_evp_max)  # (7)式左辺(係数部)
        return right / left

    # NOTE: 論文より最大時のRのみ別に計算する
    R_max = R_max_H(Pc, spec.q_rac_max, 0.001*spec.P_rac_max, spec, condi)

    Qs = np.array([spec.q_rac_min, spec.q_rac_rtd, spec.q_rac_max])
    Rs = np.array([R_minrtd, R_minrtd, R_max])

    coeffs = np.polyfit(Qs, Rs, 2)  # 二次式に近似し係数を取得
    R_poly_a2, R_poly_a1, R_poly_a0 = coeffs[0], coeffs[1], coeffs[2]
    _logger.info(f"a2: {R_poly_a2}\na1: {R_poly_a1}\na0: {R_poly_a0}")

    return R_poly_a2, R_poly_a1, R_poly_a0, Pc
