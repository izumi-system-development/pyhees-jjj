import os
import pytest
import numpy as np
# JJJ
import jjjexperiment.inputs as jjj_ipt
import jjjexperiment.underfloor_ac as jjj_ufac

class Test_床下空調時_共通:

    def test_床下空調利用時の有効面積と比率(self):
        """
        床下空調利用時の有効面積と比率
        """
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)

        # Act
        A_s_ufac_i, r_A_s_ufac = jjj_ufac.get_A_s_ufac_i(input.A_A, input.A_MR, input.A_OR)

        # Assert
        assert np.shape(A_s_ufac_i) == (12, 1)
        assert r_A_s_ufac == pytest.approx(65.4/input.A_A, rel=1e-2)
