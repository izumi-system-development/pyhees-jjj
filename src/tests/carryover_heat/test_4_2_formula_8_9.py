import numpy as np
import pytest

import pyhees.section3_1 as ld
# JJJ
import jjjexperiment.constants as jjj_consts
import jjjexperiment.carryover_heat as jjj_carryover_heat

def test_負荷バランス時の負荷_暖房_式8():
    """(8) 過剰熱量繰越を考慮した 熱損失を含む負荷バランス時の暖房負荷
    """
    # Arrange

    # [MJ/h]
    L_H_i = np.array([5.927, 2.490, 1.522, 1.462, 1.885]).reshape(-1,1)
    assert L_H_i.shape == (5, 1), "L_H_iの次数が想定外"
    # [MJ/h]
    Q_star_trs_prt_d_t_i = np.array([0.596, 0.435, 0.348, 0.283, 0.283]).reshape(-1,1)
    assert Q_star_trs_prt_d_t_i.shape == (5, 1), "Q_star_trs_prt_d_t_iの次数が想定外"

    Theta_HBR_i = np.array([20.0, 20.9, 21.0, 20.0, 20.0]).reshape(-1,1)

    # Act
    carryover = jjj_carryover_heat.calc_carryover(
            H = True, C = False,
            A_HCZ_i = np.array([ld.get_A_HCZ_R_i[i] for i in range(5)]),
            Theta_HBR_i = Theta_HBR_i,
            Theta_star_HBR = 20.0)

    L_star_H_i = jjj_carryover_heat. \
        get_L_star_H_i_2024(True, L_H_i, Q_star_trs_prt_d_t_i, carryover)

    # Assert
    assert L_star_H_i.shape == (5, 1), "L_star_H_iの次数が想定外"

    exp_L_star_H_i = np.array([6.523, 2.474, 1.469, 1.745, 2.168]).reshape(-1,1)
    np.testing.assert_almost_equal(L_star_H_i, exp_L_star_H_i, decimal=2), \
        "L_star_H_iの計算がおかしい"


@pytest.mark.skip(reason="計算例が未提供のため")
def test_負荷バランス時の負荷_冷房_式9():
    """(9) 過剰熱量繰越を考慮した 熱損失を含む負荷バランス時の冷房負荷
    """
    pass
