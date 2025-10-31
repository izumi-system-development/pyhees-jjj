import numpy as np
import pytest
from pyhees.section4_2_a import get_E_E_fan_H_d_t, get_E_E_fan_C_d_t


class TestFanPowerHeating:
    """暖房送風機消費電力のユニットテスト (式37: get_E_E_fan_H_d_t)"""

    def test_basic_calculation(self):
        """暖房送風機消費電力の基本計算テスト"""
        # Arrange
        P_fan_rtd_H = 100.0  # 定格暖房能力運転時の送風機の消費電力 [W]
        V_hs_vent_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        q_hs_H_d_t = np.zeros(8760)
        
        V_hs_vent_d_t[:3] = [50.0, 100.0, 150.0]  # 全般換気分風量 [m3/h]
        V_hs_supply_d_t[:3] = [200.0, 400.0, 600.0]  # 送風量 [m3/h]
        q_hs_H_d_t[:3] = [1000.0, 2000.0, 3000.0]  # 平均暖房能力 [W]
        V_hs_dsgn_H = 500.0  # 暖房時の設計風量 [m3/h]

        # Act
        result = get_E_E_fan_H_d_t(
            P_fan_rtd_H=P_fan_rtd_H,
            V_hs_vent_d_t=V_hs_vent_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            V_hs_dsgn_H=V_hs_dsgn_H,
            q_hs_H_d_t=q_hs_H_d_t
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert len(result) == 8760
        assert all(result >= 0)  # 消費電力は非負値であること
        assert result[0] > 0  # 最初の3時間は非ゼロ値であること
        assert result[1] > 0
        assert result[2] > 0

    def test_zero_heating_load(self):
        """暖房負荷がゼロの場合の送風機消費電力テスト"""
        # Arrange
        P_fan_rtd_H = 100.0
        V_hs_vent_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        q_hs_H_d_t = np.zeros(8760)  # 全てゼロ - 暖房負荷なし
        
        V_hs_vent_d_t[0] = 50.0
        V_hs_supply_d_t[0] = 200.0
        V_hs_dsgn_H = 500.0

        # Act
        result = get_E_E_fan_H_d_t(
            P_fan_rtd_H=P_fan_rtd_H,
            V_hs_vent_d_t=V_hs_vent_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            V_hs_dsgn_H=V_hs_dsgn_H,
            q_hs_H_d_t=q_hs_H_d_t
        )

        # Assert
        assert result[0] == 0.0  # 暖房負荷がゼロの場合、送風機消費電力もゼロになること

    def test_with_sfp_parameter(self):
        """SFPパラメータを使用した送風機消費電力計算テスト"""
        # Arrange
        P_fan_rtd_H = 100.0
        V_hs_vent_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        q_hs_H_d_t = np.zeros(8760)
        
        V_hs_vent_d_t[0] = 50.0
        V_hs_supply_d_t[0] = 200.0
        q_hs_H_d_t[0] = 1000.0
        V_hs_dsgn_H = 500.0
        f_SFP = 0.5  # 比消費電力 [W/(m3/h)]

        # Act
        result = get_E_E_fan_H_d_t(
            P_fan_rtd_H=P_fan_rtd_H,
            V_hs_vent_d_t=V_hs_vent_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            V_hs_dsgn_H=V_hs_dsgn_H,
            q_hs_H_d_t=q_hs_H_d_t,
            f_SFP=f_SFP
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert result[0] > 0


class TestFanPowerCooling:
    """冷房送風機消費電力のユニットテスト (式38: get_E_E_fan_C_d_t)"""

    def test_basic_calculation(self):
        """冷房送風機消費電力の基本計算テスト"""
        # Arrange
        P_fan_rtd_C = 120.0  # 定格冷房能力運転時の送風機の消費電力 [W]
        V_hs_vent_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        q_hs_C_d_t = np.zeros(8760)
        
        V_hs_vent_d_t[:3] = [60.0, 120.0, 180.0]  # 全般換気分風量 [m3/h]
        V_hs_supply_d_t[:3] = [250.0, 500.0, 750.0]  # 送風量 [m3/h]
        q_hs_C_d_t[:3] = [1200.0, 2400.0, 3600.0]  # 平均冷房能力 [W]
        V_hs_dsgn_C = 600.0  # 冷房時の設計風量 [m3/h]

        # Act
        result = get_E_E_fan_C_d_t(
            P_fan_rtd_C=P_fan_rtd_C,
            V_hs_vent_d_t=V_hs_vent_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            V_hs_dsgn_C=V_hs_dsgn_C,
            q_hs_C_d_t=q_hs_C_d_t
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert len(result) == 8760
        assert all(result >= 0)  # 消費電力は非負値であること
        assert result[0] > 0
        assert result[1] > 0
        assert result[2] > 0

    def test_zero_cooling_load(self):
        """冷房負荷がゼロの場合の送風機消費電力テスト"""
        # Arrange
        P_fan_rtd_C = 120.0
        V_hs_vent_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        q_hs_C_d_t = np.zeros(8760)  # 全てゼロ - 冷房負荷なし
        
        V_hs_vent_d_t[0] = 60.0
        V_hs_supply_d_t[0] = 250.0
        V_hs_dsgn_C = 600.0

        # Act
        result = get_E_E_fan_C_d_t(
            P_fan_rtd_C=P_fan_rtd_C,
            V_hs_vent_d_t=V_hs_vent_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            V_hs_dsgn_C=V_hs_dsgn_C,
            q_hs_C_d_t=q_hs_C_d_t
        )

        # Assert
        assert result[0] == 0.0  # 冷房負荷がゼロの場合、送風機消費電力もゼロになること

    def test_with_sfp_parameter(self):
        """SFPパラメータを使用した送風機消費電力計算テスト"""
        # Arrange
        P_fan_rtd_C = 120.0
        V_hs_vent_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        q_hs_C_d_t = np.zeros(8760)
        
        V_hs_vent_d_t[0] = 60.0
        V_hs_supply_d_t[0] = 250.0
        q_hs_C_d_t[0] = 1200.0
        V_hs_dsgn_C = 600.0
        f_SFP = 0.4  # 比消費電力 [W/(m3/h)]

        # Act
        result = get_E_E_fan_C_d_t(
            P_fan_rtd_C=P_fan_rtd_C,
            V_hs_vent_d_t=V_hs_vent_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            V_hs_dsgn_C=V_hs_dsgn_C,
            q_hs_C_d_t=q_hs_C_d_t,
            f_SFP=f_SFP
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert result[0] > 0


class TestFanPowerComparison:
    """暖房・冷房送風機消費電力の比較テスト"""

    def test_similar_inputs_similar_outputs(self):
        """類似の入力値で合理的な相対出力が得られることをテスト"""
        # Arrange
        P_fan_rtd = 100.0
        V_hs_vent_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        q_hs_d_t = np.zeros(8760)
        
        V_hs_vent_d_t[0] = 50.0
        V_hs_supply_d_t[0] = 200.0
        q_hs_d_t[0] = 1000.0
        V_hs_dsgn = 500.0

        # Act
        result_H = get_E_E_fan_H_d_t(
            P_fan_rtd_H=P_fan_rtd,
            V_hs_vent_d_t=V_hs_vent_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            V_hs_dsgn_H=V_hs_dsgn,
            q_hs_H_d_t=q_hs_d_t
        )

        result_C = get_E_E_fan_C_d_t(
            P_fan_rtd_C=P_fan_rtd,
            V_hs_vent_d_t=V_hs_vent_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            V_hs_dsgn_C=V_hs_dsgn,
            q_hs_C_d_t=q_hs_d_t
        )

        # Assert
        ratio = result_H[0] / result_C[0]
        assert 0.5 < ratio < 2.0  # 類似の入力に対して結果が合理的な範囲内であること
