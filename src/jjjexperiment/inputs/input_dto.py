import yaml
from pydantic import BaseModel, ValidationError

class InputDto(BaseModel):
    """直接入力されるもの"""
    A_A: float
    A_MR: float
    A_OR: float
    region: int
    A_env: float
    U_A: float
    eta_A_H: float
    eta_A_C: float

def load_input_yaml(yaml_path: str) -> InputDto:
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            input_yaml = yaml.safe_load(f)
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {yaml_path} が見つかりませんでした。")
        raise e

    try:
        input_data = InputDto(**input_yaml)
    except ValidationError as e:
        print(e.json())
        raise
    return input_data
