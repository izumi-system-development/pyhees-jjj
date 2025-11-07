import os
import pytest
import numpy as np
# JJJ
from jjjexperiment.inputs.di_container import create_injector_from_json
from jjjexperiment.inputs.common import HouseInfo
from jjjexperiment.underfloor_ac.section4_2 import get_A_s_ufac_i
from test_utils.utils import load_input_yaml

class Test_床下空調時_共通:

    def test_床下空調利用時の有効面積と比率(self):
        """
        床下空調利用時の有効面積と比率
        """
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        injector = create_injector_from_json(load_input_yaml(yaml_fullpath))

        house = injector.get(HouseInfo)

        # Act
        A_s_ufac_i, r_A_s_ufac = get_A_s_ufac_i(house.A_A, house.A_MR, house.A_OR)

        # Assert
        assert np.shape(A_s_ufac_i) == (12, 1)
        assert r_A_s_ufac == pytest.approx(65.4/house.A_A, rel=1e-2)
