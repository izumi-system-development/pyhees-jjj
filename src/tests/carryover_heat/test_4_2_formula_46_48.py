import numpy as np
import pytest

import pyhees.section3_1 as ld
# JJJ
import jjjexperiment.constants as jjj_consts
import jjjexperiment.carryover_heat as jjj_carryover_heat

# 先生から提供いただいたPDFの計算例に基づくテストです

def test_過剰熱量繰越を考慮した室温_居室_式46():
    # Arrange
    L_star_H_i = np.array([6.545, 2.474, 1.469, 1.745, 2.168]).reshape(-1,1)
    assert L_star_H_i.shape == (5, 1), "L_star_H_iの次数が想定外"

    V_supply_i = np.array([333.85, 185.46, 148.39, 120.51, 120.62]).reshape(-1,1)
    assert V_supply_i.shape == (5, 1), "V_supply_iの次数が想定外"

    Theta_supply_i = np.array([34.56, 35.21, 33.09, 31.83, 33.16]).reshape(-1,1)
    assert Theta_supply_i.shape == (5, 1), "Theta_supply_d_t_iの次数が想定外"

    A_prt_i = np.array([32.92, 24.02, 19.22, 15.61, 15.61]).reshape(-1,1)
    assert A_prt_i.shape == (5, 1), "A_prt_iの次数が想定外"

    A_HCZ_i = np.array([ld.get_A_HCZ_R_i(i) for i in range(5)]).reshape(-1,1)
    assert A_HCZ_i.shape == (5, 1), "A_HCZ_iの次数が想定外"

    Theta_HBR_before_i = np.array([20.0, 20.9, 21.0, 20.0, 20.0]).reshape(-1,1)
    assert Theta_HBR_before_i.shape == (5, 1), "Theta_HBR_iの次数が想定外"

    # Act
    Theta_HBR_i \
        = jjj_carryover_heat.get_Theta_HBR_i_2023(
            isFirst = (2==0), H = True, C = False, M = False,
            Theta_star_HBR = 20,
            V_supply_i = V_supply_i,
            Theta_supply_i = Theta_supply_i,
            U_prt = 2.17,  # W/(m2・K)
            A_prt_i = A_prt_i,
            Q = 2.6472,  # W/(m2・K)
            A_HCZ_i = A_HCZ_i,
            L_star_H_i = L_star_H_i,
            L_star_CS_i = np.zeros((5,1)),  # 暖房時のテストのため
            Theta_HBR_before_i = Theta_HBR_before_i)

    # Assert
    assert Theta_HBR_i.shape == (5, 1), "Theta_HBR_iの次数が想定外"

    # NOTE: 資料ではキャップされていないが、実装ではキャップされている
    exp_Theta_HBR_i = np.array([19.63, 21.29, 21.49, 19.97, 19.64]).reshape(-1,1)

    np.testing.assert_almost_equal(Theta_HBR_i, exp_Theta_HBR_i, decimal=2), "Theta_HBR_iの計算がおかしい"
    # assert つかないの間違えやすいので注意

def test_過剰熱量繰越を考慮した室温_非居室_式48():
    # Arrange
    # ℃
    theta_HBR_i = np.array([20.0, 20.79, 20.98, 20.0, 20.0]).reshape(-1,1)
    assert theta_HBR_i.shape == (5, 1), "theta_HBR_iの次数が想定外"
    # m3/h
    v_dash_supply_i = np.array([333.85, 185.46, 148.39, 120.51, 120.62]).reshape(-1,1)
    assert v_dash_supply_i.shape == (5, 1), "v_dash_supply_iの次数が想定外"
    v_supply_i = v_dash_supply_i
    # m2
    a_prt_i = np.array([32.92, 24.02, 19.22, 15.61, 15.61]).reshape(-1,1)
    assert a_prt_i.shape == (5, 1), "a_prt_iの次数が想定外"

    # Act
    theta_NR \
        = jjj_carryover_heat.get_Theta_NR_2023(
            isFirst = (2==0), H = True, C = False, M = False,
            Theta_star_NR = 17.68,  # ℃
            Theta_star_HBR = 20.0,  # ℃
            Theta_HBR_i = theta_HBR_i,
            A_NR = 38.93,  # m2
            V_vent_l_NR = 0.0,  # m3/h
            V_dash_supply_i = v_dash_supply_i,
            V_supply_i = v_supply_i,
            U_prt = 2.17, # W/(m2・K)
            A_prt_i = a_prt_i,
            Q = 2.6472,  # W/m2
            Theta_NR_before = 17.88  # ℃
            )

    # Assert
    # NOTE: 資料ではキャップされていないが、実装ではキャップされている
    exp_theta_NR = 17.94  # ℃
    np.testing.assert_almost_equal(theta_NR, exp_theta_NR, decimal=2)
