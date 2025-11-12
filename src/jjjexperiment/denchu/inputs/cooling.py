from dataclasses import dataclass

from jjjexperiment.denchu.utils import absolute_humid

@dataclass
class RealInnerCondition:
    """実測室内機吸込み空気条件"""

    Theta_rac_real_inner: float = 0.0
    """実測室内機吸込み空気温度 [℃]"""
    RH_rac_real_inner: float = 0.0
    """実測室内機吸込み空気相対湿度 [%]"""

    @classmethod
    def from_dict(cls, data: dict) -> 'RealInnerCondition':
        return cls(
            Theta_rac_real_inner=float(data.get('Theta_rac_real_inner', 0.0)),
            RH_rac_real_inner=float(data.get('RH_rac_real_inner', 0.0))
        )

@dataclass
class DenchuCatalogSpecification:
    """電中研カタログ仕様"""

    name: str = ""
    """機器名"""
    P_rac_min: float = 0.0
    """JIS条件での消費電力 最小 [W]"""
    P_rac_rtd: float = 0.0
    """JIS条件での消費電力 定格 [W]"""
    P_rac_max: float = 0.0
    """JIS条件での消費電力 最大 [W]"""

    # NOTE: 室内から除去するエネルギー = 冷房能力 (論文より)
    q_rac_min: float = 0.0
    """JIS条件での熱処理能力 最小 [kW]"""
    q_rac_rtd: float = 0.0
    """JIS条件での熱処理能力 定格 [kW]"""
    q_rac_max: float = 0.0
    """JIS条件での熱処理能力 最大 [kW]"""

    V_rac_inner: float = 0.0
    """室内機の吸込み空気量 [m3/min]"""
    V_rac_outer: float = 0.0
    """室外機の吸込み空気量 [m3/min]"""

    # カタログスペック計測時の温熱環境条件 JIS指定値
    Theta_rac_inner: float = 0.0
    """室内機の吸込み空気温度 [℃]"""
    Theta_rac_outer: float = 0.0
    """室外機の吸込み空気温度 [℃]"""
    X_rac_inner: float = 0.0
    """室内機の吸込み空気の絶対湿度 [g/kg DA]"""
    X_rac_outer: float = 0.0
    """室外機の吸込み空気の絶対湿度 [g/kg DA]"""

    # NOTE: 下記は冷暖で逆になる
    @property
    def T_evp(self) -> float:
        """蒸発器と接する空気の温度 [℃]"""
        return self.Theta_rac_inner
    @property
    def T_cnd(self) -> float:
        """凝縮器と接する空気の温度 [℃]"""
        return self.Theta_rac_outer
    @property
    def X_evp(self) -> float:
        """蒸発器と接する空気の絶対湿度 [g/kg DA]"""
        return self.X_rac_inner
    @property
    def X_cnd(self) -> float:
        """凝縮器と接する空気の絶対湿度 [g/kg DA]"""
        return self.X_rac_outer

    @classmethod
    def from_dict(cls, data: dict) -> 'DenchuCatalogSpecification':
        return cls(
            P_rac_min=float(data.get('P_rac_pub_min', 0.0)),
            P_rac_rtd=float(data.get('P_rac_pub_rtd', 0.0)),
            P_rac_max=float(data.get('P_rac_pub_max', 0.0)),
            q_rac_min=float(data.get('q_rac_pub_min', 0.0)),
            q_rac_rtd=float(data.get('q_rac_pub_rtd', 0.0)),
            q_rac_max=float(data.get('q_rac_pub_max', 0.0)),
            V_rac_inner=float(data.get('V_rac_pub_inner', 0.0)),
            V_rac_outer=float(data.get('V_rac_pub_outer', 0.0)),
            Theta_rac_inner=float(data.get('Theta_rac_pub_inner', 0.0)),
            Theta_rac_outer=float(data.get('Theta_rac_pub_outer', 0.0)),
            X_rac_inner=float(absolute_humid(data.get('RH_rac_pub_inner', 0.0), data.get('Theta_rac_pub_inner', 0.0))),
            X_rac_outer=float(absolute_humid(data.get('RH_rac_pub_outer', 0.0), data.get('Theta_rac_pub_outer', 0.0))),
        )

    def outputDataFrame(self, data_frame):
        """csv出力用のデータフレーム"""
        data_frame.loc[DenchuCatalogSpecification.P_rac_min.__doc__] = [self.P_rac_min]
        data_frame.loc[DenchuCatalogSpecification.P_rac_rtd.__doc__] = [self.P_rac_rtd]
        data_frame.loc[DenchuCatalogSpecification.P_rac_max.__doc__] = [self.P_rac_max]
        data_frame.loc[DenchuCatalogSpecification.q_rac_min.__doc__] = [self.q_rac_min]
        data_frame.loc[DenchuCatalogSpecification.q_rac_rtd.__doc__] = [self.q_rac_rtd]
        data_frame.loc[DenchuCatalogSpecification.q_rac_max.__doc__] = [self.q_rac_max]
        data_frame.loc[DenchuCatalogSpecification.V_rac_inner.__doc__] = [self.V_rac_inner]
        data_frame.loc[DenchuCatalogSpecification.V_rac_outer.__doc__] = [self.V_rac_outer]
        data_frame.loc[DenchuCatalogSpecification.T_evp.__doc__] = [self.T_evp]
        data_frame.loc[DenchuCatalogSpecification.T_cnd.__doc__] = [self.T_cnd]
        data_frame.loc[DenchuCatalogSpecification.X_evp.__doc__] = [self.X_evp]
        data_frame.loc[DenchuCatalogSpecification.X_cnd.__doc__] = [self.X_cnd]
        return data_frame
