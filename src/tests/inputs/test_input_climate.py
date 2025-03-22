import numpy as np
import pytest
from typing import List

from jjjexperiment.common import JJJ_HCM

@pytest.mark.usefixtures('climate_entity')
class Test_Input_Climate:

    yaml_filename = "inputs/test_input.yaml"

    def test_get_J_d_t(self, climate_entity):
        """
        get_J_d_t をテスト
        """
        # Act
        J_d_t = climate_entity.get_J_d_t()
        # Assert
        assert J_d_t is not None
        assert np.shape(J_d_t) == (8760,)

    def test_get_X_ex_d_t(self, climate_entity):
        """
        get_X_ex_d_t をテスト
        """
        # Act
        X_ex_d_t = climate_entity.get_X_ex_d_t()
        # Assert
        assert X_ex_d_t is not None
        assert len(X_ex_d_t) == 8760

    def test_get_Theta_ex_d_t(self, climate_entity):
        """
        get_Theta_ex_d_t をテスト
        """
        # Act
        Theta_ex_d_t = climate_entity.get_Theta_ex_d_t()
        # Assert
        assert Theta_ex_d_t is not None
        assert len(Theta_ex_d_t) == 8760

    def test_get_HCM_d_t(self, climate_entity):
        """
        get_HCM_d_t をテスト
        """
        # Act
        HCM_d_t: List[JJJ_HCM] = climate_entity.get_HCM_d_t()
        # Assert
        assert HCM_d_t is not None
        assert len(HCM_d_t) == 8760
        assert all([x is not None for x in HCM_d_t])

    def test_get_g_avg(self, climate_entity):
        """
        get_g_avg をテスト
        """
        # Act
        Theta_g_avg = climate_entity.get_Theta_g_avg()
        # Assert
        assert Theta_g_avg is not None
        assert Theta_g_avg == pytest.approx(15.68, rel=1e-2)
