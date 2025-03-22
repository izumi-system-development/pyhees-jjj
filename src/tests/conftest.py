import os
import pytest
import numpy as np

import pyhees.section4_2 as dc
# JJJ
import jjjexperiment.inputs as jjj_ipt
import jjjexperiment.underfloor_ac as jjj_ufac

@pytest.fixture(scope='class')
def climate_entity(request) -> jjj_ipt.ClimateEntity:
    # Arrange
    yaml_filename = request.cls.yaml_filename  # クラスのメンバー名
    current_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(current_dir, yaml_filename)
    input_data = jjj_ipt.load_input_yaml(yaml_path)
    climate = jjj_ipt.ClimateEntity(input_data.region)
    return climate

@pytest.fixture(scope='class')
def environment_entity(request) -> jjj_ipt.EnvironmentEntity:
    # Arrange
    yaml_filename = request.cls.yaml_filename  # クラスのメンバー名
    current_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(current_dir, yaml_filename)
    input_data = jjj_ipt.load_input_yaml(yaml_path)
    environment = jjj_ipt.EnvironmentEntity(input_data)
    return environment

@pytest.fixture
def Q_hat_hs_d_t():
    yaml_fullpath = os.path.join(os.path.dirname(__file__), 'inputs/test_input.yaml')
    input = jjj_ipt.load_input_yaml(yaml_fullpath)

    environment = jjj_ipt.EnvironmentEntity(input)
    climate = jjj_ipt.ClimateEntity(input.region)

    V_vent_l_d_t = np.array(dc.get_V_vent_l_d_t(
        dc.get_V_vent_l_NR_d_t(),
        dc.get_V_vent_l_OR_d_t(),
        dc.get_V_vent_l_MR_d_t()
    ))

    sum_V_vent_g_i = np.sum(environment.get_V_vent_g_i())
    HCM=np.array(climate.get_HCM_d_t())

    vector_Q_hat_hs = np.vectorize(jjj_ufac.calc_Q_hat_hs)
    Q_hat_hs_d_t = vector_Q_hat_hs(
        Q=environment.get_Q(),
        A_A=input.A_A,
        V_vent_l=V_vent_l_d_t,
        sum_V_vent_g_i=sum_V_vent_g_i,
        mu_H=environment.get_mu_H(),
        mu_C=environment.get_mu_C(),
        J=climate.get_J_d_t(),
        q_gen=environment.get_q_gen_d_t(),
        n_p=environment.get_n_p_d_t(),
        q_p_H=dc.get_q_p_H(),
        q_p_CS=dc.get_q_p_CS(),
        q_p_CL=dc.get_q_p_CL(),
        X_ex=climate.get_X_ex_d_t(),
        w_gen=environment.get_w_gen_d_t(),
        Theta_ex=climate.get_Theta_ex_d_t(),
        L_wtr=dc.get_L_wtr(),
        HCM=HCM
    )

    return Q_hat_hs_d_t
