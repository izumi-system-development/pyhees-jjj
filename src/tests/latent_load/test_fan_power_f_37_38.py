import numpy as np
from jjjexperiment.latent_load.section4_2_a import get_E_E_fan_H_d_t, get_E_E_fan_C_d_t

class Test暖房送風機消費電力:
    """暖房送風機消費電力のユニットテスト (式37: get_E_E_fan_H_d_t)"""

    def test_基本計算_正常値(self):
        """暖房送風機消費電力の基本計算テスト"""
        # Arrange
        V_hs_vent_d_t = np.zeros(8760)
        q_hs_H_d_t = np.zeros(8760)
        f_SFP = 0.4  # ファンの比消費電力 [W/(m3・h)]

        V_hs_vent_d_t[0] = 50.0    # 全般換気分風量 [m3/h] - 暖房期
        q_hs_H_d_t[0] = 1000.0     # 平均暖房能力 [W] - 暖房期

        # Act
        result = get_E_E_fan_H_d_t(
            V_hs_vent_d_t=V_hs_vent_d_t,
            q_hs_H_d_t=q_hs_H_d_t,
            f_SFP=f_SFP
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert len(result) == 8760
        assert all(result >= 0)  # 消費電力は非負値であること
        assert result[0] > 0     # 暖房期では正の値になること

    def test_境界値_ゼロ負荷(self):
        """暖房負荷がゼロの場合の送風機消費電力テスト"""
        # Arrange
        V_hs_vent_d_t = np.zeros(8760)
        q_hs_H_d_t = np.zeros(8760)  # 全てゼロ - 暖房負荷なし
        f_SFP = 0.4

        V_hs_vent_d_t[0] = 50.0

        # Act
        result = get_E_E_fan_H_d_t(
            V_hs_vent_d_t=V_hs_vent_d_t,
            q_hs_H_d_t=q_hs_H_d_t,
            f_SFP=f_SFP
        )

        # Assert
        assert result[0] == 0.0  # 暖房負荷がゼロの場合、送風機消費電力もゼロになること

    def test_パラメータ変動_SFP値(self):
        """SFPパラメータを使用した送風機消費電力計算テスト"""
        # Arrange & Act
        V_hs_vent_d_t = np.zeros(8760)
        q_hs_H_d_t = np.zeros(8760)
        
        V_hs_vent_d_t[0] = 50.0
        q_hs_H_d_t[0] = 1000.0
        f_SFP = 0.5  # 比消費電力 [W/(m3/h)]

        result = get_E_E_fan_H_d_t(
            V_hs_vent_d_t=V_hs_vent_d_t,
            q_hs_H_d_t=q_hs_H_d_t,
            f_SFP=f_SFP
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert result[0] > 0


class Test冷房送風機消費電力:
    """冷房送風機消費電力のユニットテスト (式38: get_E_E_fan_C_d_t)"""

    def test_基本計算_正常値(self):
        """冷房送風機消費電力の基本計算テスト"""
        # Arrange
        V_hs_vent_d_t = np.zeros(8760)
        q_hs_C_d_t = np.zeros(8760)
        f_SFP = 0.4  # ファンの比消費電力 [W/(m3/h)]

        # 冷房期のインデックス（夏期）
        V_hs_vent_d_t[4848] = 60.0   # 全般換気分風量 [m3/h]
        q_hs_C_d_t[4848] = 1200.0    # 平均冷房能力 [W]

        # Act
        result = get_E_E_fan_C_d_t(
            V_hs_vent_d_t=V_hs_vent_d_t,
            q_hs_C_d_t=q_hs_C_d_t,
            f_SFP=f_SFP
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert len(result) == 8760
        assert all(result >= 0)  # 消費電力は非負値であること
        assert result[4848] > 0  # 冷房期では正の値

    def test_境界値_ゼロ負荷(self):
        """冷房負荷がゼロの場合の送風機消費電力テスト"""
        # Arrange
        V_hs_vent_d_t = np.zeros(8760)
        q_hs_C_d_t = np.zeros(8760)  # 全てゼロ - 冷房負荷なし
        f_SFP = 0.4

        V_hs_vent_d_t[4848] = 60.0

        # Act
        result = get_E_E_fan_C_d_t(
            V_hs_vent_d_t=V_hs_vent_d_t,
            q_hs_C_d_t=q_hs_C_d_t,
            f_SFP=f_SFP
        )

        # Assert
        assert result[4848] == 0.0  # 冷房負荷がゼロの場合、送風機消費電力もゼロになること

    def test_パラメータ変動_SFP値(self):
        """SFPパラメータを使用した送風機消費電力計算テスト"""
        # Arrange & Act
        V_hs_vent_d_t = np.zeros(8760)
        q_hs_C_d_t = np.zeros(8760)
        
        V_hs_vent_d_t[4848] = 60.0
        q_hs_C_d_t[4848] = 1200.0
        f_SFP = 0.4  # 比消費電力 [W/(m3/h)]

        result = get_E_E_fan_C_d_t(
            V_hs_vent_d_t=V_hs_vent_d_t,
            q_hs_C_d_t=q_hs_C_d_t,
            f_SFP=f_SFP
        )

        # Assert
        assert isinstance(result, np.ndarray)
        assert result[4848] > 0


class Test暖冷房送風機比較:
    """暖房・冷房送風機消費電力の比較テスト"""

    def test_季節別動作確認(self):
        """季節に応じた適切な動作をテスト"""
        # Arrange & Act
        V_hs_vent_d_t = np.zeros(8760)
        q_hs_H_d_t = np.zeros(8760)
        q_hs_C_d_t = np.zeros(8760)
        f_SFP = 0.4

        # 暖房期（冬）
        V_hs_vent_d_t[0] = 50.0
        q_hs_H_d_t[0] = 1000.0
        
        # 冷房期（夏）
        V_hs_vent_d_t[4848] = 50.0
        q_hs_C_d_t[4848] = 1000.0

        result_H = get_E_E_fan_H_d_t(
            V_hs_vent_d_t=V_hs_vent_d_t,
            q_hs_H_d_t=q_hs_H_d_t,
            f_SFP=f_SFP
        )

        result_C = get_E_E_fan_C_d_t(
            V_hs_vent_d_t=V_hs_vent_d_t,
            q_hs_C_d_t=q_hs_C_d_t,
            f_SFP=f_SFP
        )

        # Assert
        assert result_H[0] > 0     # 暖房期は暖房ファン動作
        assert result_C[4848] > 0  # 冷房期は冷房ファン動作
        assert result_H[4848] == 0  # 冷房期は暖房ファン停止
        assert result_C[0] == 0     # 暖房期は冷房ファン停止