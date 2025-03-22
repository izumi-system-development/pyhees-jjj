import os
import pytest
import numpy as np

# JJJ
from jjjexperiment.common import *
from jjjexperiment.options import *
from jjjexperiment.di_container import *
from jjjexperiment.app_config import *
import jjjexperiment.inputs as jjj_ipt
import jjjexperiment.underfloor_ac as jjj_ufac

class Test_床下空調時_式46_式48:

    @classmethod
    def setup_class(cls):
        """テストクラス共通設定"""
        app_config = injector.get(AppConfig)
        app_config.new_ufac_flg = 床下空調ロジック.変更する.value

    def test_式46_時点計算例(self):
        """
        (46) 暖冷房区画iの実際の居室の室温
        """
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)
        environment = jjj_ipt.EnvironmentEntity(input)

        A_s_ufac_i, _ = jjj_ufac.get_A_s_ufac_i(input.A_A, input.A_MR, input.A_OR)
        A_HCZ_i = environment.get_A_HCZ_i().reshape(-1, 1)

        # Act
        Theta_HBR_i = jjj_ufac.get_Theta_HBR_i(
            Theta_star_HBR = 20.0,
            V_supply_i = np.array([342.3, 190.2, 152.0, 123.6, 123.7]).reshape(-1, 1),
            Theta_supply_i = np.array([24.89, 24.89, 36.78, 35.39, 36.85]).reshape(-1, 1),
            U_prt = 2.17,
            A_prt_i = np.array([32.92, 24.02, 19.22, 15.61, 15.61]).reshape(-1, 1),
            Q = 2.6472,
            A_HCZ_i = A_HCZ_i[:5, :],
            L_star_H_i = np.array([3.639, 1.308, 1.881, 1.752, 2.178]).reshape(-1, 1),
            L_star_CS_i = np.array([0, 0, 0, 0, 0]).reshape(-1, 1),
            HCM = JJJ_HCM.H,
            A_s_ufac_i = A_s_ufac_i[:5, :],
            Theta_uf = 24.89
        )

        # Assert
        assert Theta_HBR_i[0, 0] == pytest.approx(19.62, abs=1e-2)
        assert Theta_HBR_i[1, 0] == pytest.approx(20.65, abs=1e-2)
        assert Theta_HBR_i[2, 0] == pytest.approx(22.60, abs=1e-2)
        assert Theta_HBR_i[3, 0] == pytest.approx(21.45, abs=1e-2)
        assert Theta_HBR_i[4, 0] == pytest.approx(20.90, abs=1e-2)


    def test_式48_時点計算例(self):
        """
        (48) 実際の非居室の室温
        """
        # Arrange

        # Act
        Theta_NR = jjj_ufac.get_Theta_NR(
            Theta_star_NR = 19.40,
            Theta_star_HBR = 20.0,
            # 上テストのアサートと同一値
            Theta_HBR_i = np.array([19.62, 20.65, 22.60, 21.45, 20.90]).reshape(-1, 1),
            A_NR = 38.93,
            V_vent_l_NR = 0,
            V_dash_supply_i = np.array([342.3, 190.2, 152.0, 123.6, 123.7]).reshape(-1, 1),
            V_supply_i = np.array([342.3, 190.2, 152.0, 123.6, 123.7]).reshape(-1, 1),
            U_prt = 2.17,
            A_prt_i = np.array([32.92, 24.02, 19.22, 15.61, 15.61]).reshape(-1, 1),
            Q = 2.6472,
            Theta_uf = 24.89
        )
        # Assert
        assert Theta_NR == pytest.approx(20.65, abs=1e-2)
