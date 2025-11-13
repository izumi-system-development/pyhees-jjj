import numpy as np
import pytest
import pyhees.section3_1 as ld
# JJJ
import jjjexperiment.constants as jjj_consts
import jjjexperiment.carryover_heat as jjj_carryover_heat

# 熱容量の計算をテストする

@pytest.mark.parametrize(["exp_C_BR_i"], [
        pytest.param(jjj_consts.C1_BR_R_i),  # 熱容量1(空間・什器のみ)
    ])
def test_熱容量取得_居室_標準住戸(exp_C_BR_i):
    """ 居室の面積が標準住戸通りであれば、熱容量も標準住戸通りとなる
    """
    # Arrange
    A_HCZ_i = np.array([ld.get_A_HCZ_R_i[i] for i in range(5)]).reshape(-1, 1)  # (5,) -> (5,1)

    # Act
    C_BR_i = jjj_carryover_heat.get_C_BR_i(A_HCZ_i)

    # Assert
    exp_C_BR_i = np.array(exp_C_BR_i) \
                    .reshape(-1,1)  # (5,) -> (5,1)
    assert np.all(C_BR_i == exp_C_BR_i),  \
        "熱容量が標準住戸通りでない"


@pytest.mark.parametrize(["exp_C_NR"], [
        pytest.param(jjj_consts.C1_NR_R),  # 熱容量1(空間・什器のみ)
    ])
def test_熱容量取得_非居室_標準住戸(exp_C_NR):
    """ 非居室の面積が標準住戸通りであれば、熱容量も標準住戸通りとなる
    """
    # Arrange & Act
    C_NR = jjj_carryover_heat.get_C_NR(jjj_consts.A_NR_R)

    # Assert
    assert exp_C_NR == C_NR, \
        "熱容量が標準住戸通りでない"
