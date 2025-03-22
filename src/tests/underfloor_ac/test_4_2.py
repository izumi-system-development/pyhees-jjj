import os
import numpy as np
import pyhees.section3_1 as ld
import pyhees.section3_1_d as uf
import pyhees.section3_1_e as algo
import pyhees.section3_2 as gihi
import pyhees.section4_1 as HC
import pyhees.section4_2 as dc

# JJJ
from jjjexperiment.input import get_solarheat
import jjjexperiment.inputs as jjj_ipt
import jjjexperiment.underfloor_ac as jjj_ufac
import pytest

class Test_熱損失を含む負荷バランス時の暖冷房負荷:

    def test_既存関数の計算(self):
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
