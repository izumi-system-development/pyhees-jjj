import yaml
from typing import Optional
from pydantic import BaseModel, ValidationError

class H_A(BaseModel):
    """暖房方式"""
    type: int
    input_V_hs_dsgn_H: Optional[int] = 1  # 入力しない
    """設計風量の手動入力の有効・無効"""
    V_hs_dsgn_H: Optional[float] = 1500.0  # 規定値
    """直接取得せず HAエンティティ経由で取得"""
    q_hs_rtd_H: Optional[float] = 10000.0  # 規定値
    V_fan_rtd_H: Optional[float] = None
    input: int
    """機器仕様の入力の有無"""
    # 機器仕様手動入力する時
    q_hs_rtd_H: Optional[float] = None
    P_hs_rtd_H: Optional[float] = None
    V_fan_rtd_H: Optional[float] = None
    P_fan_rtd_H: Optional[float] = None
    q_hs_min_H: Optional[float] = None
    q_hs_mid_H: Optional[float] = None
    V_fan_mid_H: Optional[float] = None
    P_fan_rtd_H: Optional[float] = None
    P_hs_rtd_H: Optional[float] = None
    # 下記は電中研モデルしか利用しない
    q_rac_min_H: Optional[float] = None
    q_rac_rtd_H: Optional[float] = None
    q_rac_max_H: Optional[float] = None
    P_rac_min_H: Optional[float] = None
    P_rac_rtd_H: Optional[float] = None
    P_rac_max_H: Optional[float] = None
    V_rac_inner_H: Optional[float] = None
    V_rac_outer_H: Optional[float] = None
    Theta_RH_rac_inner_pub_H: Optional[float] = None
    Theta_RH_rac_outer_pub_H: Optional[float] = None
    RH_rac_inner_pub_H: Optional[float] = None
    RH_rac_outer_pub_H: Optional[float] = None


class C_A(BaseModel):
    """冷房方式"""
    type: int
    input_V_hs_dsgn_C: Optional[int] = 1  # 入力しない
    """設計風量の手動入力の有効・無効"""
    V_hs_dsgn_C: Optional[float] = 1500.0  # 規定値
    """直接取得せず CAエンティティ経由で取得"""
    q_hs_rtd_C: Optional[float] = 10000.0  # 規定値
    V_fan_rtd_C: Optional[float] = None
    input: Optional[int] = 1
    """機器仕様の入力の有無"""

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
