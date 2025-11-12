import pyhees.section4_2_b as dc_spec
from .ac_setting import HeatingAcSetting, CoolingAcSetting
from .options import 機器仕様手動入力タイプ


class HeatQuantity:
    """暖房量計算エンティティ - クリーンデータクラスパターン"""
    
    def __init__(self, ac_setting: HeatingAcSetting, region: int, A_A: float):
        self.ac_setting = ac_setting
        self.region = region
        self.A_A = A_A
    
    @property
    def q_hs_rtd(self) -> float:
        if self.ac_setting.input_mode == 機器仕様手動入力タイプ.入力しない:
            return dc_spec.get_q_hs_rtd_H(self.region, self.A_A)
        elif self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.定格能力試験の値を入力する,
            機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する
        ]:
            assert self.ac_setting.q_hs_rtd_input is not None, "q_hs_rtd_input required"
            return self.ac_setting.q_hs_rtd_input
        return 0.0
    
    @property
    def q_hs_min(self) -> float:
        return dc_spec.get_q_hs_min_H(self.q_hs_rtd)
    
    @property
    def q_hs_mid(self) -> float:
        if self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.入力しない,
            機器仕様手動入力タイプ.定格能力試験の値を入力する
        ]:
            return dc_spec.get_q_hs_mid_H(self.q_hs_rtd)
        elif self.ac_setting.input_mode == 機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する:
            assert self.ac_setting.q_hs_mid_input is not None, "q_hs_mid_input required"
            return self.ac_setting.q_hs_mid_input
        return 0.0
    
    @property
    def P_hs_rtd(self) -> float:
        if self.ac_setting.input_mode == 機器仕様手動入力タイプ.入力しない:
            return dc_spec.get_P_hs_rtd_H(self.q_hs_rtd)
        elif self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.定格能力試験の値を入力する,
            機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する
        ]:
            assert self.ac_setting.P_hs_rtd_input is not None, "P_hs_rtd_input required"
            return self.ac_setting.P_hs_rtd_input
        return 0.0
    
    @property
    def P_hs_mid(self) -> float:
        if self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.入力しない,
            機器仕様手動入力タイプ.定格能力試験の値を入力する
        ]:
            return float('nan')
        elif self.ac_setting.input_mode == 機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する:
            assert self.ac_setting.P_hs_mid_input is not None, "P_hs_mid_input required"
            return self.ac_setting.P_hs_mid_input
        return 0.0
    
    @property
    def V_fan_rtd(self) -> float:
        if self.ac_setting.input_mode == 機器仕様手動入力タイプ.入力しない:
            return dc_spec.get_V_fan_rtd_H(self.q_hs_rtd)
        elif self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.定格能力試験の値を入力する,
            機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する
        ]:
            assert self.ac_setting.V_fan_rtd_input is not None, "V_fan_rtd_input required"
            return self.ac_setting.V_fan_rtd_input
        return 0.0
    
    @property
    def V_fan_mid(self) -> float:
        if self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.入力しない,
            機器仕様手動入力タイプ.定格能力試験の値を入力する
        ]:
            return dc_spec.get_V_fan_mid_H(self.q_hs_mid)
        elif self.ac_setting.input_mode == 機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する:
            assert self.ac_setting.V_fan_mid_input is not None, "V_fan_mid_input required"
            return self.ac_setting.V_fan_mid_input
        return 0.0
    
    @property
    def P_fan_rtd(self) -> float:
        if self.ac_setting.input_mode == 機器仕様手動入力タイプ.入力しない:
            return dc_spec.get_P_fan_rtd_H(self.V_fan_rtd)
        elif self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.定格能力試験の値を入力する,
            機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する
        ]:
            assert self.ac_setting.P_fan_rtd_input is not None, "P_fan_rtd_input required"
            return self.ac_setting.P_fan_rtd_input
        return 0.0
    
    @property
    def P_fan_mid(self) -> float:
        if self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.入力しない,
            機器仕様手動入力タイプ.定格能力試験の値を入力する
        ]:
            return dc_spec.get_P_fan_mid_H(self.V_fan_mid)
        elif self.ac_setting.input_mode == 機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する:
            assert self.ac_setting.P_fan_mid_input is not None, "P_fan_mid_input required"
            return self.ac_setting.P_fan_mid_input
        return 0.0


class CoolQuantity:
    """冷房量計算エンティティ - クリーンデータクラスパターン"""
    
    def __init__(self, ac_setting: CoolingAcSetting, region: int, A_A: float):
        self.ac_setting = ac_setting
        self.region = region
        self.A_A = A_A
    
    @property
    def q_hs_rtd(self) -> float:
        if self.ac_setting.input_mode == 機器仕様手動入力タイプ.入力しない:
            return dc_spec.get_q_hs_rtd_C(self.region, self.A_A)
        elif self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.定格能力試験の値を入力する,
            機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する
        ]:
            assert self.ac_setting.q_hs_rtd_input is not None, "q_hs_rtd_input required"
            return self.ac_setting.q_hs_rtd_input
        return 0.0
    
    @property
    def q_hs_min(self) -> float:
        return dc_spec.get_q_hs_min_C(self.q_hs_rtd)
    
    @property
    def q_hs_mid(self) -> float:
        if self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.入力しない,
            機器仕様手動入力タイプ.定格能力試験の値を入力する
        ]:
            return dc_spec.get_q_hs_mid_C(self.q_hs_rtd)
        elif self.ac_setting.input_mode == 機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する:
            assert self.ac_setting.q_hs_mid_input is not None, "q_hs_mid_input required"
            return self.ac_setting.q_hs_mid_input
        return 0.0
    
    @property
    def P_hs_rtd(self) -> float:
        if self.ac_setting.input_mode == 機器仕様手動入力タイプ.入力しない:
            return dc_spec.get_P_hs_rtd_C(self.q_hs_rtd)
        elif self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.定格能力試験の値を入力する,
            機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する
        ]:
            assert self.ac_setting.P_hs_rtd_input is not None, "P_hs_rtd_input required"
            return self.ac_setting.P_hs_rtd_input
        return 0.0
    
    @property
    def P_hs_mid(self) -> float:
        if self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.入力しない,
            機器仕様手動入力タイプ.定格能力試験の値を入力する
        ]:
            return float('nan')
        elif self.ac_setting.input_mode == 機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する:
            assert self.ac_setting.P_hs_mid_input is not None, "P_hs_mid_input required"
            return self.ac_setting.P_hs_mid_input
        return 0.0
    
    @property
    def V_fan_rtd(self) -> float:
        if self.ac_setting.input_mode == 機器仕様手動入力タイプ.入力しない:
            return dc_spec.get_V_fan_rtd_C(self.q_hs_rtd)
        elif self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.定格能力試験の値を入力する,
            機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する
        ]:
            assert self.ac_setting.V_fan_rtd_input is not None, "V_fan_rtd_input required"
            return self.ac_setting.V_fan_rtd_input
        return 0.0
    
    @property
    def V_fan_mid(self) -> float:
        if self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.入力しない,
            機器仕様手動入力タイプ.定格能力試験の値を入力する
        ]:
            return dc_spec.get_V_fan_mid_C(self.q_hs_mid)
        elif self.ac_setting.input_mode == 機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する:
            assert self.ac_setting.V_fan_mid_input is not None, "V_fan_mid_input required"
            return self.ac_setting.V_fan_mid_input
        return 0.0
    
    @property
    def P_fan_rtd(self) -> float:
        if self.ac_setting.input_mode == 機器仕様手動入力タイプ.入力しない:
            return dc_spec.get_P_fan_rtd_C(self.V_fan_rtd)
        elif self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.定格能力試験の値を入力する,
            機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する
        ]:
            assert self.ac_setting.P_fan_rtd_input is not None, "P_fan_rtd_input required"
            return self.ac_setting.P_fan_rtd_input
        return 0.0
    
    @property
    def P_fan_mid(self) -> float:
        if self.ac_setting.input_mode in [
            機器仕様手動入力タイプ.入力しない,
            機器仕様手動入力タイプ.定格能力試験の値を入力する
        ]:
            return dc_spec.get_P_fan_mid_C(self.V_fan_mid)
        elif self.ac_setting.input_mode == 機器仕様手動入力タイプ.定格能力試験と中間能力試験の値を入力する:
            assert self.ac_setting.P_fan_mid_input is not None, "P_fan_mid_input required"
            return self.ac_setting.P_fan_mid_input
        return 0.0