import os
import pytest

import jjjexperiment.inputs as jjj_ipt

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
