import pytest
from jjjexperiment.ac_min_volume_input.section4_2_a import get_E_E_fan_d_t
from jjjexperiment.inputs.options import ファン消費電力算定方法

def test_get_E_E_fan_linear_method():
    """直線近似法のテスト"""
    result = get_E_E_fan_d_t(
        E_E_fan_logic=ファン消費電力算定方法.直線近似法,
        P_fan_rtd=1000.0,
        V_hs_vent_d_t=100.0,
        V_hs_supply_d_t=500.0,
        V_hs_dsgn=800.0,
        q_hs_d_t=5000.0,
        E_E_fan_min=50.0
    )
    assert result > 0
    assert isinstance(result, float)

def test_get_E_E_fan_cubic_method():
    """風量三乗近似法のテスト"""
    result = get_E_E_fan_d_t(
        E_E_fan_logic=ファン消費電力算定方法.風量三乗近似法,
        P_fan_rtd=1000.0,
        V_hs_vent_d_t=100.0,
        V_hs_supply_d_t=500.0,
        V_hs_dsgn=800.0,
        q_hs_d_t=5000.0,
        E_E_fan_min=50.0
    )
    assert result > 0
    assert isinstance(result, float)

def test_get_E_E_fan_thermo_off():
    """サーモOFF時のテスト"""
    result = get_E_E_fan_d_t(
        E_E_fan_logic=ファン消費電力算定方法.直線近似法,
        P_fan_rtd=1000.0,
        V_hs_vent_d_t=100.0,
        V_hs_supply_d_t=500.0,
        V_hs_dsgn=800.0,
        q_hs_d_t=0.0,  # サーモOFF
        E_E_fan_min=50.0
    )
    assert result >= 0
