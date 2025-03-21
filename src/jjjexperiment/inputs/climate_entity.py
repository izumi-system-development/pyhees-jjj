import numpy as np
from typing import Any
from nptyping import Float64, NDArray, Shape

import pyhees.section3_1_e as algo
import pyhees.section4_2 as dc
import pyhees.section11_1 as rgn
import pyhees.section11_2 as slr
# JJJ
from jjjexperiment.common import *

class ClimateEntity:
    """ region に関するデータを保持するクラス """

    def __init__(self, region: int):
        self.region = region
        self.climate = rgn.load_climate(region)

    def get_J_d_t(self) -> NDArray[Shape['8760'], Float64]:
        J_d_t = slr.calc_I_s_d_t(0, 0, rgn.get_climate_df(self.climate))
        return J_d_t

    def get_X_ex_d_t(self) -> NDArray[Shape['8760'], Float64]:
        X_ex_d_t = rgn.get_X_ex(self.climate)
        return X_ex_d_t

    def get_Theta_ex_d_t(self) -> NDArray[Shape['8760'], Float64]:
        Theta_ex_d_t = rgn.get_Theta_ex(self.climate)
        return Theta_ex_d_t

    def get_Theta_g_avg(self) -> float:
        return algo.get_Theta_g_avg(self.get_Theta_ex_d_t())

    def get_HCM_d_t(self) -> NDArray[Shape['8760'], Any]:
        H, C, M = dc.get_season_array_d_t(self.region)
        HCM = []
        for i in range(len(H)):
            if H[i]:
                HCM.append(JJJ_HCM.H)
            elif C[i]:
                HCM.append(JJJ_HCM.C)
            elif M[i]:
                HCM.append(JJJ_HCM.M)
            else:
                raise ValueError
        # 事後条件
        assert len(HCM) == 8760

        return np.array(HCM)

    def get_psi(self, Q: float) -> float:
        """
        Ψ値を計算
        Args:
            Q: 当該住戸の熱損失係数 [W/m2*K]
        Returns:
            psi: 基礎の線熱貫流率Ψ [W/m2*K]
        """
        # CHECK: psi,phi 異なるが大丈夫か要確認
        return algo.get_phi(self.region, Q)

    def get_U_s_vert(self, Q: float) -> float:
        """
        暖冷房負荷計算時に想定した床の熱貫流率 [W/m2*K]
        Args:
            Q: 当該住戸の熱損失係数 [W/m2*K]
        Returns:
            U_s_vert: 暖冷房負荷計算時に想定した床の熱貫流率 [W/m2*K]
        """
        return algo.get_U_s_vert(self.region, Q)
