from typing import List
import numpy as np
from nptyping import Float64, NDArray, Shape

import pyhees.section4_2 as dc
import pyhees.section11_1 as rgn
import pyhees.section11_2 as slr

# JJJ
from jjjexperiment.common import *

class ClimateEntity:

    def __init__(self, region: int):
        self.__region = region
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

    def get_HCM_d_t(self) -> List[JJJ_HCM]:
        H, C, M = dc.get_season_array_d_t(self.__region)
        HCM = [None] * len(H)
        for i in range(len(H)):
            if H[i]:
                HCM[i] = JJJ_HCM.H
            elif C[i]:
                HCM[i] = JJJ_HCM.C
            elif M[i]:
                HCM[i] = JJJ_HCM.M
            else:
                raise ValueError
        # 事後条件
        assert len(HCM) == 8760
        assert all([x is not None for x in HCM])

        return np.array(HCM)
