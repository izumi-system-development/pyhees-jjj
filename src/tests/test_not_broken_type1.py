import pytest
import json
import copy
import math

from jjjexperiment.main import calc
from os import path

from test_utils.utils import  \
    expected_inputs, expected_result_type1, INPUT_SAMPLE_TYPE1_PATH

class Test既存計算維持_入力値切替_方式1:
    """ 既存計算が壊れていないことのテスト
        暖房・冷房ともに「ダクト式セントラル空調機」
    """
    _inputs: dict = json.load(open(INPUT_SAMPLE_TYPE1_PATH, 'r'))

    def test_前提確認_入力値(self, expected_inputs):
        """ テストコードが想定しているインプットデータかどうか確認
        """
        result = calc(self._inputs, test_mode=True)

        assert result['TInput'].q_rtd_C == expected_inputs.q_rtd_C
        assert result['TInput'].q_rtd_H == expected_inputs.q_rtd_H
        assert result['TInput'].q_max_C == expected_inputs.q_max_C
        assert result['TInput'].q_max_H == expected_inputs.q_max_H
        assert result['TInput'].e_rtd_C == expected_inputs.e_rtd_C
        assert result['TInput'].e_rtd_H == expected_inputs.e_rtd_H

    def test_前提確認_計算結果(self, expected_result_type1):
        """ ベースとしている結果が確かであることを確認
        """
        result = calc(self._inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C == expected_result_type1.E_C

    def test_入力値入替_01(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            最大暖房出力時の熱源機の出口における空気温度の最大値の上限値
            Theta_hs_out_max_H_d_t_limit
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["Theta_hs_out_max_H_d_t_limit"] = 47.5

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 36312.73469516181)

    def test_入力値入替_02(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            最大冷房出力時の熱源機の出口における空気温度の最低値の下限値
            Theta_hs_out_min_C_d_t_limit
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["Theta_hs_out_min_C_d_t_limit"] = 18.2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 14499.62278132686)

    def test_入力値入替_03(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            デフロストに関する暖房出力補正係数（ダクトセントラル空調機）
            C_df_H_d_t_defrost_ductcentral
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_df_H_d_t_defrost_ductcentral"] = 0.88

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 35890.90098587334)

    def test_入力値入替_04(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            デフロスト発生外気温度（ダクトセントラル空調機）
            defrost_temp_ductcentral
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["defrost_temp_ductcentral"] = 6.2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 36546.573126677504)

    def test_入力値入替_05(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            デフロスト発生外気相対湿度（ダクトセントラル空調機）
            defrost_humid_ductcentral
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["defrost_humid_ductcentral"] = 77

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 36611.49578865069)

    def test_入力値入替_06(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            ダクトiの線熱損失係数
            phi_i
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["phi_i"] = 0.52

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 36646.91339321118)
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 14803.44514208752)

    def test_入力値入替_07(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            暖房時の送風機の設計風量に関する係数
            C_V_fan_dsgn_H
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_V_fan_dsgn_H"] = 0.82

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 35836.748455098634)

    def test_入力値入替_08(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            冷房時の送風機の設計風量に関する係数
            C_V_fan_dsgn_C
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_V_fan_dsgn_C"] = 0.81

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_C, 14646.69148373989)
        assert result['TValue'].E_C != expected_result_type1.E_C

    def test_入力値入替_09(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            デフロストに関する暖房出力補正係数（ルームエアコンディショナー）
            C_df_H_d_t_defrost_rac
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫?
        inputs["C_df_H_d_t_defrost_rac"] = 0.88

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C == expected_result_type1.E_C

    def test_入力値入替_10(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            デフロスト発生外気温度（ルームエアコンディショナー）
            defrost_temp_rac
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫?
        inputs["defrost_temp_rac"] = 5.2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C == expected_result_type1.E_C

    def test_入力値入替_11(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            デフロスト発生外気相対湿度（ルームエアコンディショナー）
            defrost_humid_rac
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫?
        inputs["defrost_humid_rac"] = 82

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C == expected_result_type1.E_C

    def test_入力値入替_12(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            室内機吸い込み湿度に関する冷房出力補正係数
            C_hm_C
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫?
        inputs["C_hm_C"] = 1.32

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C == expected_result_type1.E_C

    def test_入力値入替_13(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            定格冷房能力の最大値
            q_rtd_C_limit
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫?
        inputs["q_rtd_C_limit"] = 3500

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C == expected_result_type1.E_C

    def test_入力値入替_14(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            面積の合計 [m2]
            A_A
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["A_A"] = 135.92

        result = calc(inputs, test_mode=True)

        assert math.isclose(result['TValue'].E_H, 40461.6302264345)
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_C, 14832.537841444147)
        assert result['TValue'].E_C != expected_result_type1.E_C

    def test_入力値入替_15(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            主たる居室の面積 [m2]
            A_MR
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["A_MR"] = 68.29

        result = calc(inputs, test_mode=True)

        assert math.isclose(result['TValue'].E_H, 42391.84140416556)
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_C, 21443.382718755827)
        assert result['TValue'].E_C != expected_result_type1.E_C

    def test_入力値入替_16(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            その他の居室の面積[m2]
            A_OR
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["A_OR"] = 123.456

        result = calc(inputs, test_mode=True)

        assert math.isclose(result['TValue'].E_H, 49036.33660346446)
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_C, 24217.967340540887)
        assert result['TValue'].E_C != expected_result_type1.E_C

    def test_入力値入替_17(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            地域区分
            region
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["region"] = 1

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 141367.326695553)
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 3151.6467125592953)

    def test_入力値入替_18(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            外皮面積 [m2]
            A_env
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["A_env"] = 333.332

        result = calc(inputs, test_mode=True)

        assert math.isclose(result['TValue'].E_H, 42086.82025871831)
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_C, 14867.887750721573)
        assert result['TValue'].E_C != expected_result_type1.E_C

    def test_入力値入替_19(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            外皮平均熱貫流率 UA [W/(m2・K)]
            U_A
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["U_A"] = 1.03

        result = calc(inputs, test_mode=True)

        assert math.isclose(result['TValue'].E_H, 44911.46410023861)
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_C, 14005.505611991277)
        assert result['TValue'].E_C != expected_result_type1.E_C

    def test_入力値入替_20(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            冷房期平均日射熱取得率ηAC
            eta_A_C
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["eta_A_C"] = 3.3

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 16358.465844105795)

    def test_入力値入替_21(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            暖房期平均日射熱取得率ηAH
            eta_A_H
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["eta_A_H"] = 3.9

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_H, 40516.98524230055)
        assert result['TValue'].E_H != expected_result_type1.E_H

    def test_入力値入替_22(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            床下空間を経由して外気を導入する換気方式の利用 （☐：評価しない or ☑：評価する）
            underfloor_ventilation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["underfloor_ventilation"] = "2"

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 34056.175244458456)
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 13038.13319064152)

    def test_入力値入替_23(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            外気が経由する床下の面積の割合 [%]
            r_A_ufvnt
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫?
        inputs["r_A_ufvnt"] = 85.0

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C == expected_result_type1.E_C

    def test_入力値入替_24(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            床下空間の断熱 （☐：断熱区画外 or ☑：断熱区画内）
            underfloor_insulation
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫?
        inputs["underfloor_insulation"] = "2"

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C == expected_result_type1.E_C

    def test_入力値入替_25(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            空調空気を床下を通して給気する （☐：床下を通して給気しない or ☑：床下を通して給気する）
            underfloor_air_conditioning_air_supply
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["underfloor_air_conditioning_air_supply"] = "2"

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 59669.99880864711)
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 18714.44515829817)

    def test_入力値入替_26(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            地盤またはそれを覆う基礎の表面熱伝達抵抗 [(m2・K)/W]
            R_g
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫? 0.15 -> 0.19
        inputs["R_g"] = 0.19

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C == expected_result_type1.E_C

    def test_入力値入替_27(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            全体風量を固定する （☐：固定しない or ☑：固定する）
            hs_CAV
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["hs_CAV"] = "2"

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 34061.44658403281)

    def test_入力値入替_H1(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            ダクトが通過する空間 （全てもしくは一部が断熱区画外である or 全て断熱区画内である）
            H_A_duct_insulation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["H_A"]["duct_insulation"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 34608.193798931)

    def test_入力値入替_H2(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            VAV方式 （採用しない or 採用する）
            H_A_VAV
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["H_A"]["VAV"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 36291.25164821471)

    def test_入力値入替_H3(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            全般換気機能 （あり or なし）
            H_A_general_ventilation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["H_A"]["general_ventilation"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 37064.91576192836)

    def test_入力値入替_H4(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            設計風量 [m3/h]（入力する場合のみ）
            H_A_V_hs_dsgn_H
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["H_A"]["input_V_hs_dsgn_H"] = 2
        inputs["H_A"]["V_hs_dsgn_H"] = 1820

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 32622.96874682381)

    def test_入力値入替_H5_方式1(self, expected_inputs, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            暖房の機器仕様を入力する1
        """
        inputs = copy.deepcopy(self._inputs)
        # 機器仕様の入力（入力しない or 定格能力試験の値を入力する or 定格能力試験と中間能力試験の値を入力する）
        inputs["H_A"]["input"] = 2  # ★ 定格能力試験の値を入力する
        # ▼ 入力する場合のみ
        inputs["H_A"]["q_hs_rtd_H"] = 30000.0     # 定格暖房能力試験 能力 [W]
        inputs["H_A"]["q_hs_mid_H"] = 15000.0     # 中間暖房能力試験 能力 [W]
        inputs["H_A"]["P_hs_rtd_H"] = 8570        # 定格暖房能力試験 消費電力 [W]
        inputs["H_A"]["P_hs_mid_H"] = 4300        # 中間暖房能力試験 消費電力 [W]
        inputs["H_A"]["V_fan_rtd_H"] = 50.0 * 60  # 定格暖房能力試験 風量 [m3/h]
        inputs["H_A"]["V_fan_mid_H"] = 25.0 * 60  # 中間暖房能力試験 風量 [m3/h]
        inputs["H_A"]["P_fan_rtd_H"] = 350        # 定格暖房能力試験 室内側送風機の消費電力 [W]
        inputs["H_A"]["P_fan_mid_H"] = 170        # 中間暖房能力試験 室内側送風機の消費電力 [W]

        result = calc(inputs, test_mode=True)

        assert result['TInput'].q_rtd_C == expected_inputs.q_rtd_C
        assert result['TInput'].q_rtd_H == expected_inputs.q_rtd_H
        assert result['TInput'].q_max_C == expected_inputs.q_max_C
        assert result['TInput'].q_max_H == expected_inputs.q_max_H
        assert result['TInput'].e_rtd_C == expected_inputs.e_rtd_C
        assert result['TInput'].e_rtd_H == expected_inputs.e_rtd_H

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_H, 81575.50253836498)
        assert result['TValue'].E_H != expected_result_type1.E_H

    def test_入力値入替_H6_方式1(self, expected_inputs, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            暖房の機器仕様を入力する2
        """
        inputs = copy.deepcopy(self._inputs)
        # 機器仕様の入力（入力しない or 定格能力試験の値を入力する or 定格能力試験と中間能力試験の値を入力する）
        inputs["H_A"]["input"] = 2
        # ▼ 入力する場合のみ
        inputs["H_A"]["q_hs_rtd_H"] = 27500.0     # 定格暖房能力試験 能力 [W]
        inputs["H_A"]["q_hs_mid_H"] = 13000.0     # 中間暖房能力試験 能力 [W]
        inputs["H_A"]["P_hs_rtd_H"] = 7100        # 定格暖房能力試験 消費電力 [W]
        inputs["H_A"]["P_hs_mid_H"] = 3450        # 中間暖房能力試験 消費電力 [W]
        inputs["H_A"]["V_fan_rtd_H"] = 54.0 * 60  # 定格暖房能力試験 風量 [m3/h]
        inputs["H_A"]["V_fan_mid_H"] = 22.0 * 60  # 中間暖房能力試験 風量 [m3/h]
        inputs["H_A"]["P_fan_rtd_H"] = 400        # 定格暖房能力試験 室内側送風機の消費電力 [W]
        inputs["H_A"]["P_fan_mid_H"] = 210        # 中間暖房能力試験 室内側送風機の消費電力 [W]

        result = calc(inputs, test_mode=True)

        assert result['TInput'].q_rtd_C == expected_inputs.q_rtd_C
        assert result['TInput'].q_rtd_H == expected_inputs.q_rtd_H
        assert result['TInput'].q_max_C == expected_inputs.q_max_C
        assert result['TInput'].q_max_H == expected_inputs.q_max_H
        assert result['TInput'].e_rtd_C == expected_inputs.e_rtd_C
        assert result['TInput'].e_rtd_H == expected_inputs.e_rtd_H

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 72987.18193043352)

    def test_入力値入替_R1(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            ダクトが通過する空間（全てもしくは一部が断熱区画外である or 全て断熱区画内である）
            C_A_duct_insulation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_A"]["duct_insulation"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 14980.637500033028)

    def test_入力値入替_R2(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            VAV方式 (採用しない or 採用する）
            C_A_VAV
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_A"]["VAV"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 12852.724729450114)

    def test_入力値入替_R3(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            全般換気機能（あり or なし）
            C_A_general_ventilation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_A"]["general_ventilation"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 15191.971001329612)

    def test_入力値入替_R4(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            設計風量 [m3/h]（入力する場合のみ）
            C_A_V_hs_dsgn_C
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_A"]["input_V_hs_dsgn_C"] = 2
        inputs["C_A"]["V_hs_dsgn_C"] = 1650

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 13915.09558491048)

    def test_入力値入替_R5_方式1(self, expected_inputs, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            冷房の機器仕様を入力する1
        """
        inputs = copy.deepcopy(self._inputs)
        # 機器仕様の入力（入力しない or 定格能力試験の値を入力する or 定格能力試験と中間能力試験の値を入力する）
        inputs["C_A"]["input"] = 2
        # ▼ 入力する場合のみ
        inputs["C_A"]["q_hs_rtd_C"] = 30000.0     # 定格冷房能力試験 能力 [W]
        inputs["C_A"]["q_hs_mid_C"] = 15000.0     # 中間冷房能力試験 能力 [W]
        inputs["C_A"]["P_hs_rtd_C"] = 8570        # 定格冷房能力試験 消費電力 [W]
        inputs["C_A"]["P_hs_mid_C"] = 4300        # 中間冷房能力試験 消費電力 [W]
        inputs["C_A"]["V_fan_rtd_C"] = 50.0 * 60  # 定格冷房能力試験 風量 [m3/h]
        inputs["C_A"]["V_fan_mid_C"] = 25.0 * 60  # 中間冷房能力試験 風量 [m3/h]
        inputs["C_A"]["P_fan_rtd_C"] = 350        # 定格冷房能力試験 室内側送風機の消費電力 [W]
        inputs["C_A"]["P_fan_mid_C"] = 170        # 中間冷房能力試験 室内側送風機の消費電力 [W]

        result = calc(inputs, test_mode=True)

        assert result['TInput'].q_rtd_C == expected_inputs.q_rtd_C
        assert result['TInput'].q_rtd_H == expected_inputs.q_rtd_H
        assert result['TInput'].q_max_C == expected_inputs.q_max_C
        assert result['TInput'].q_max_H == expected_inputs.q_max_H
        assert result['TInput'].e_rtd_C == expected_inputs.e_rtd_C
        assert result['TInput'].e_rtd_H == expected_inputs.e_rtd_H

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 19187.38971453038)

    def test_入力値入替_R6_方式1(self, expected_inputs, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            冷房の機器仕様を入力する2
        """
        # 機器仕様の入力（入力しない or 定格能力試験の値を入力する or 定格能力試験と中間能力試験の値を入力する）
        inputs = copy.deepcopy(self._inputs)
        # ▼ 入力する場合のみ
        inputs["C_A"]["input"] = 2
        inputs["C_A"]["q_hs_rtd_C"] = 27500.0     # 定格冷房能力試験 能力 [W]
        inputs["C_A"]["q_hs_mid_C"] = 13000.0     # 中間冷房能力試験 能力 [W]
        inputs["C_A"]["P_hs_rtd_C"] = 7100        # 定格冷房能力試験 消費電力 [W]
        inputs["C_A"]["P_hs_mid_C"] = 3450        # 中間冷房能力試験 消費電力 [W]
        inputs["C_A"]["V_fan_rtd_C"] = 54.0 * 60  # 定格冷房能力試験 風量 [m3/h]
        inputs["C_A"]["V_fan_mid_C"] = 22.0 * 60  # 中間冷房能力試験 風量 [m3/h]
        inputs["C_A"]["P_fan_rtd_C"] = 400        # 定格冷房能力試験 室内側送風機の消費電力 [W]
        inputs["C_A"]["P_fan_mid_C"] = 210        # 中間冷房能力試験 室内側送風機の消費電力 [W]

        result = calc(inputs, test_mode=True)

        assert result['TInput'].q_rtd_C == expected_inputs.q_rtd_C
        assert result['TInput'].q_rtd_H == expected_inputs.q_rtd_H
        assert result['TInput'].q_max_C == expected_inputs.q_max_C
        assert result['TInput'].q_max_H == expected_inputs.q_max_H
        assert result['TInput'].e_rtd_C == expected_inputs.e_rtd_C
        assert result['TInput'].e_rtd_H == expected_inputs.e_rtd_H

        assert result['TValue'].E_H == expected_result_type1.E_H
        assert result['TValue'].E_C != expected_result_type1.E_C
        assert math.isclose(result['TValue'].E_C, 19238.129853353777)

    def test_入力値入替_HEX1(self, expected_result_type1):
        """ 以前のプログラムと同じ計算結果になる
            温度交換効率（設置する場合のみ）
            etr_t
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["HEX"]["install"] = 2
        inputs["HEX"]["etr_t"] = 0.3

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type1.E_C
        assert result['TValue'].E_H != expected_result_type1.E_H
        assert math.isclose(result['TValue'].E_H, 34414.79844612079)
