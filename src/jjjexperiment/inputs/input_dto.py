import yaml
from typing import Optional
from pydantic import BaseModel, ValidationError

class H_A(BaseModel):
    """暖房方式"""
    input: Optional[int] = 1  # 規定値
    V_hs_dsgn_H: Optional[float] = 1500  # 規定値
    q_hs_rtd_H: Optional[float] = 10000  # 規定値

class C_A(BaseModel):
    """冷房方式"""
    input: Optional[int] = 1  # 規定値
    V_hs_dsgn_C: Optional[float] = 1500  # 規定値
    q_hs_rtd_C: Optional[float] = 10000  # 規定値

class InputDto(BaseModel):
    """直接入力されるもの"""
    A_A: float
    A_MR: float
    A_OR: float
    region: int
    sol_region: Optional[int] = None
    A_env: float
    U_A: float
    eta_A_H: float
    eta_A_C: float
    R_g: float
    TS: bool
    r_A_ufvnt: Optional[float] = None
    hs_CAV: Optional[bool] = False
    H_A: H_A
    C_A: C_A
    U_s_vert: float = 2.223
    """暖冷房負荷計算時に想定した床の熱貫流率 [W/m2・K]"""
    psi: float = 0.846
    """基礎(床チャンバー側面)の線熱貫流率φ [W/m・K]"""

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
