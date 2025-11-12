import numpy as np
from pyhees.section4_2_a import get_q_hs_H_d_t, get_q_hs_C_d_t

class TestHeatingLoad:
    """暖房負荷計算のユニットテスト (式1: get_q_hs_H_d_t)"""

    def test_basic_heating_calculation(self):
        """暖房負荷の基本計算テスト"""
        # Arrange
        Theta_hs_out_d_t = np.zeros(8760)
        Theta_hs_in_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        C_df_H_d_t = np.ones(8760)  # デフロスト補正係数

        # 暖房期の代表的な条件を設定
        Theta_hs_out_d_t[0] = 35.0  # 出口温度 [℃]
        Theta_hs_in_d_t[0] = 20.0   # 入口温度 [℃]
        V_hs_supply_d_t[0] = 300.0  # 送風量 [m3/h]
        region = 6  # 地域区分

        # Act
        result = get_q_hs_H_d_t(
            Theta_hs_out_d_t=Theta_hs_out_d_t,
            Theta_hs_in_d_t=Theta_hs_in_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            C_df_H_d_t=C_df_H_d_t,
            region=region
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert len(result) == 8760
        assert all(result >= 0)  # 暖房能力は非負値であること
        assert result[0] > 0     # 暖房期では正の値になること

    def test_zero_temperature_difference(self):
        """温度差がゼロの場合の暖房負荷テスト"""
        # Arrange
        Theta_hs_out_d_t = np.zeros(8760)
        Theta_hs_in_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        C_df_H_d_t = np.ones(8760)

        # 出口・入口温度を同じに設定（温度差ゼロ）
        Theta_hs_out_d_t[0] = 20.0
        Theta_hs_in_d_t[0] = 20.0
        V_hs_supply_d_t[0] = 300.0
        region = 6

        # Act
        result = get_q_hs_H_d_t(
            Theta_hs_out_d_t=Theta_hs_out_d_t,
            Theta_hs_in_d_t=Theta_hs_in_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            C_df_H_d_t=C_df_H_d_t,
            region=region
        )

        # Assert
        assert result[0] == 0.0  # 温度差がゼロの場合、暖房能力もゼロになること

    def test_defrost_correction_factor(self):
        """デフロスト補正係数の影響テスト"""
        # Arrange
        Theta_hs_out_d_t = np.zeros(8760)
        Theta_hs_in_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)
        C_df_H_d_t = np.ones(8760)

        Theta_hs_out_d_t[0] = 35.0
        Theta_hs_in_d_t[0] = 20.0
        V_hs_supply_d_t[0] = 300.0
        C_df_H_d_t[0] = 0.8  # デフロスト補正係数を0.8に設定
        region = 6

        # Act
        result = get_q_hs_H_d_t(
            Theta_hs_out_d_t=Theta_hs_out_d_t,
            Theta_hs_in_d_t=Theta_hs_in_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            C_df_H_d_t=C_df_H_d_t,
            region=region
        )

        # Assert
        assert result[0] > 0  # デフロスト補正があっても正の値になること


class TestCoolingLoad:
    """冷房負荷計算のユニットテスト (式2: get_q_hs_C_d_t)"""

    def test_basic_cooling_calculation(self):
        """冷房負荷の基本計算テスト"""
        # Arrange
        Theta_hs_out_d_t = np.zeros(8760)
        Theta_hs_in_d_t = np.zeros(8760)
        X_hs_out_d_t = np.zeros(8760)
        X_hs_in_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)

        # 冷房期の代表的な条件を設定（夏期：6-8月頃）
        summer_index = 4848  # 夏期の代表時刻
        Theta_hs_out_d_t[summer_index] = 15.0  # 出口温度 [℃]
        Theta_hs_in_d_t[summer_index] = 27.0   # 入口温度 [℃]
        X_hs_out_d_t[summer_index] = 0.008     # 出口絶対湿度 [kg/kg(DA)]
        X_hs_in_d_t[summer_index] = 0.012      # 入口絶対湿度 [kg/kg(DA)]
        V_hs_supply_d_t[summer_index] = 400.0  # 送風量 [m3/h]
        region = 6  # 地域区分

        # Act
        result = get_q_hs_C_d_t(
            Theta_hs_out_d_t=Theta_hs_out_d_t,
            Theta_hs_in_d_t=Theta_hs_in_d_t,
            X_hs_out_d_t=X_hs_out_d_t,
            X_hs_in_d_t=X_hs_in_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            region=region
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert len(result) == 8760
        assert all(result >= 0)  # 冷房能力は非負値であること
        assert result[summer_index] > 0  # 冷房期では正の値になること

    def test_zero_temperature_difference_cooling(self):
        """温度差がゼロの場合の冷房負荷テスト"""
        # Arrange
        Theta_hs_out_d_t = np.zeros(8760)
        Theta_hs_in_d_t = np.zeros(8760)
        X_hs_out_d_t = np.zeros(8760)
        X_hs_in_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)

        summer_index = 4848
        # 出口・入口温度を同じに設定（温度差ゼロ）
        Theta_hs_out_d_t[summer_index] = 25.0
        Theta_hs_in_d_t[summer_index] = 25.0
        X_hs_out_d_t[summer_index] = 0.010
        X_hs_in_d_t[summer_index] = 0.010
        V_hs_supply_d_t[summer_index] = 400.0
        region = 6

        # Act
        result = get_q_hs_C_d_t(
            Theta_hs_out_d_t=Theta_hs_out_d_t,
            Theta_hs_in_d_t=Theta_hs_in_d_t,
            X_hs_out_d_t=X_hs_out_d_t,
            X_hs_in_d_t=X_hs_in_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            region=region
        )

        # Assert
        assert result[summer_index] == 0.0  # 温度・湿度差がゼロの場合、冷房能力もゼロになること

    def test_humidity_difference_effect(self):
        """湿度差の影響テスト"""
        # Arrange
        Theta_hs_out_d_t = np.zeros(8760)
        Theta_hs_in_d_t = np.zeros(8760)
        X_hs_out_d_t = np.zeros(8760)
        X_hs_in_d_t = np.zeros(8760)
        V_hs_supply_d_t = np.zeros(8760)

        summer_index = 4848
        Theta_hs_out_d_t[summer_index] = 15.0  # 温度差あり
        Theta_hs_in_d_t[summer_index] = 27.0
        X_hs_out_d_t[summer_index] = 0.006     # 湿度差を大きく設定
        X_hs_in_d_t[summer_index] = 0.015
        V_hs_supply_d_t[summer_index] = 400.0
        region = 6

        # Act
        result = get_q_hs_C_d_t(
            Theta_hs_out_d_t=Theta_hs_out_d_t,
            Theta_hs_in_d_t=Theta_hs_in_d_t,
            X_hs_out_d_t=X_hs_out_d_t,
            X_hs_in_d_t=X_hs_in_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            region=region
        )

        # Assert
        assert result[summer_index] > 0  # 湿度差がある場合、潜熱負荷も含めて正の値になること


class TestHeatingCoolingComparison:
    """暖房・冷房負荷の比較テスト"""

    def test_seasonal_behavior(self):
        """季節による動作の違いをテスト"""
        # Arrange
        # 暖房負荷用パラメータ
        Theta_hs_out_H = np.zeros(8760)
        Theta_hs_in_H = np.zeros(8760)
        V_hs_supply_H = np.zeros(8760)
        C_df_H_d_t = np.ones(8760)

        # 冷房負荷用パラメータ
        Theta_hs_out_C = np.zeros(8760)
        Theta_hs_in_C = np.zeros(8760)
        X_hs_out_C = np.zeros(8760)
        X_hs_in_C = np.zeros(8760)
        V_hs_supply_C = np.zeros(8760)

        # 冬期条件（暖房）
        winter_index = 100
        Theta_hs_out_H[winter_index] = 35.0
        Theta_hs_in_H[winter_index] = 20.0
        V_hs_supply_H[winter_index] = 300.0

        # 夏期条件（冷房）
        summer_index = 4848
        Theta_hs_out_C[summer_index] = 15.0
        Theta_hs_in_C[summer_index] = 27.0
        X_hs_out_C[summer_index] = 0.008
        X_hs_in_C[summer_index] = 0.012
        V_hs_supply_C[summer_index] = 400.0

        region = 6

        # Act
        heating_result = get_q_hs_H_d_t(
            Theta_hs_out_d_t=Theta_hs_out_H,
            Theta_hs_in_d_t=Theta_hs_in_H,
            V_hs_supply_d_t=V_hs_supply_H,
            C_df_H_d_t=C_df_H_d_t,
            region=region
        )

        cooling_result = get_q_hs_C_d_t(
            Theta_hs_out_d_t=Theta_hs_out_C,
            Theta_hs_in_d_t=Theta_hs_in_C,
            X_hs_out_d_t=X_hs_out_C,
            X_hs_in_d_t=X_hs_in_C,
            V_hs_supply_d_t=V_hs_supply_C,
            region=region
        )

        # Assert
        assert heating_result[winter_index] > 0  # 冬期は暖房負荷が発生
        assert cooling_result[summer_index] > 0  # 夏期は冷房負荷が発生
        assert heating_result[summer_index] == 0  # 夏期は暖房負荷ゼロ
        assert cooling_result[winter_index] == 0  # 冬期は冷房負荷ゼロ
