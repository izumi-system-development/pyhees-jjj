import numpy as np
from jjjexperiment.v_min_input.section4_2_a import get_E_E_fan_d_t
from jjjexperiment.inputs.options import ファン消費電力算定方法

def test_get_E_E_fan_linear_method():
    """直線近似法のテスト"""
    result = get_E_E_fan_d_t(
        E_E_fan_logic=ファン消費電力算定方法.直線近似法,
        P_fan_rtd=1000.0,
        V_hs_vent_d_t=np.repeat(100.0, 24 * 365),
        V_hs_supply_d_t=np.repeat(500.0, 24 * 365),
        V_hs_dsgn=800.0,
        q_hs_d_t=np.repeat(5000.0, 24 * 365),
        E_E_fan_min=50.0
    )
    assert result.sum() > 0
    assert isinstance(result, np.ndarray)
    assert result.shape == (24 * 365,)

def test_get_E_E_fan_cubic_method():
    """風量三乗近似法のテスト"""
    result = get_E_E_fan_d_t(
        E_E_fan_logic=ファン消費電力算定方法.風量三乗近似法,
        P_fan_rtd=1000.0,
        V_hs_vent_d_t=np.repeat(100.0, 24 * 365),
        V_hs_supply_d_t=np.repeat(500.0, 24 * 365),
        V_hs_dsgn=800.0,
        q_hs_d_t=np.repeat(5000.0, 24 * 365),
        E_E_fan_min=50.0
    )
    assert result.sum() > 0
    assert isinstance(result, np.ndarray)
    assert result.shape == (24 * 365,)

def test_get_E_E_fan_thermo_off():
    """サーモOFF時のテスト"""
    result = get_E_E_fan_d_t(
        E_E_fan_logic=ファン消費電力算定方法.直線近似法,
        P_fan_rtd=1000.0,
        V_hs_vent_d_t=np.repeat(100.0, 24 * 365),
        V_hs_supply_d_t=np.repeat(500.0, 24 * 365),
        V_hs_dsgn=800.0,
        q_hs_d_t=np.repeat(0.0, 24 * 365),  # サーモOFF
        E_E_fan_min=50.0
    )
    assert result.sum() == 0
    assert isinstance(result, np.ndarray)
    assert result.shape == (24 * 365,)
