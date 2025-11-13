import os
import pytest
import numpy as np

import pyhees.section4_2 as dc
# JJJ
from jjjexperiment.inputs.di_container import create_injector_from_json
from jjjexperiment.inputs.common import HouseInfo, OuterSkin
from jjjexperiment.inputs.climate_service import ClimateService
from jjjexperiment.inputs.environment_service import EnvironmentService

import jjjexperiment.underfloor_ac.inputs as jjj_ufac_ipt
from jjjexperiment.underfloor_ac.section4_2_f40 import calc_Q_hat_hs

from test_utils.utils import load_input_yaml

@pytest.fixture(scope='class')
def climate_entity(request) -> ClimateService:
    # Arrange
    yaml_filename = request.cls.yaml_filename  # クラスのメンバー名
    current_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(current_dir, yaml_filename)
    injector = create_injector_from_json(load_input_yaml(yaml_path))

    house_info = injector.get(HouseInfo)
    new_ufac = injector.get(jjj_ufac_ipt.UnderfloorAc)

    return ClimateService(house_info.region, new_ufac)

@pytest.fixture(scope='class')
def environment_entity(request) -> EnvironmentService:
    # Arrange
    yaml_filename = request.cls.yaml_filename  # クラスのメンバー名
    current_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(current_dir, yaml_filename)
    injector = create_injector_from_json(load_input_yaml(yaml_path))

    house = injector.get(HouseInfo)
    skin = injector.get(OuterSkin)
    return EnvironmentService(house, skin)

@pytest.fixture
def Q_hat_hs_d_t():
    """(40) 熱源機の風量を計算するための熱源機の出力"""
    yaml_fullpath = os.path.join(os.path.dirname(__file__), 'inputs/test_input.yaml')
    injector = create_injector_from_json(load_input_yaml(yaml_fullpath))

    house = injector.get(HouseInfo)
    skin = injector.get(OuterSkin)
    new_ufac = injector.get(jjj_ufac_ipt.UnderfloorAc)

    environment = EnvironmentService(house, skin)
    climate = ClimateService(house.region, new_ufac)

    V_vent_l_d_t = np.array(dc.get_V_vent_l_d_t(
        dc.get_V_vent_l_NR_d_t(),
        dc.get_V_vent_l_OR_d_t(),
        dc.get_V_vent_l_MR_d_t()
    ))

    sum_V_vent_g_i = np.sum(environment.get_V_vent_g_i())
    HCM=np.array(climate.get_HCM_d_t())

    vector_Q_hat_hs = np.vectorize(calc_Q_hat_hs)
    Q_hat_hs_d_t = vector_Q_hat_hs(
        Q=environment.get_Q(),
        A_A=house.A_A,
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
