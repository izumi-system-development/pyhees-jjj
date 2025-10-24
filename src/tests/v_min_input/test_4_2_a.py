import pytest
from jjjexperiment.ac_min_volume_input.section4_2_a import get_E_E_fan
from jjjexperiment.options import ファン消費電力算定方法

def test_get_E_E_fan_linear_method():
    """直線近似法のテスト"""
    result = get_E_E_fan(
        E_E_fan_logic=ファン消費電力算定方法.直線近似法,
        P_fan_rtd=1000.0,
        V_hs_vent=100.0,
        V_hs_supply=500.0,
        V_hs_dsgn=800.0,
        q_hs=5000.0,
        E_E_fan_min=50.0
    )
    assert result > 0
    assert isinstance(result, float)

def test_get_E_E_fan_cubic_method():
    """風量三乗近似法のテスト"""
    result = get_E_E_fan(
        E_E_fan_logic=ファン消費電力算定方法.風量三乗近似法,
        P_fan_rtd=1000.0,
        V_hs_vent=100.0,
        V_hs_supply=500.0,
        V_hs_dsgn=800.0,
        q_hs=5000.0,
        E_E_fan_min=50.0
    )
    assert result > 0
    assert isinstance(result, float)

def test_get_E_E_fan_thermo_off():
    """サーモOFF時のテスト"""
    result = get_E_E_fan(
        E_E_fan_logic=ファン消費電力算定方法.直線近似法,
        P_fan_rtd=1000.0,
        V_hs_vent=100.0,
        V_hs_supply=500.0,
        V_hs_dsgn=800.0,
        q_hs=0.0,  # サーモOFF
        E_E_fan_min=50.0
    )
    assert result >= 0
