from math import exp, log

ATM_AIR_PRESSURE = 1013.25
""" 大気圧[hPa] """
BF = 0.2  # NOTE: 論文内では0.2に固定
""" Bypass-Factor """

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
