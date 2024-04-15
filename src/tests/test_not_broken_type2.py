import pytest
import json
import copy
import math

from jjjexperiment.main import calc
from os import path

from test_utils.utils import  \
    expected_inputs, expected_result_type2, INPUT_SAMPLE_TYPE2_PATH

class Test既存計算維持_入力値切替_方式2:
    """ 既存計算が壊れていないことのテスト
        暖房・冷房ともに「ルームエアコンディショナ活用型全館空調」
    """
    _inputs: dict = json.load(open(path.join(path.dirname(__file__), INPUT_SAMPLE_TYPE2_PATH), 'r'))

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

    def test_前提確認_計算結果(self, expected_result_type2):
        """ ベースとしている結果が確かであることを確認
        """
        result = calc(self._inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C == expected_result_type2.E_C

    def test_入力値入替_01(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            最大暖房出力時の熱源機の出口における空気温度の最大値の上限値
            Theta_hs_out_max_H_d_t_limit
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["Theta_hs_out_max_H_d_t_limit"] = 47.5

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 40813.23277369657)

    def test_入力値入替_02(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            最大冷房出力時の熱源機の出口における空気温度の最低値の下限値
            Theta_hs_out_min_C_d_t_limit
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["Theta_hs_out_min_C_d_t_limit"] = 18.2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 14178.967016020626)

    def test_入力値入替_03(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            デフロストに関する暖房出力補正係数（ダクトセントラル空調機）
            C_df_H_d_t_defrost_ductcentral
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_df_H_d_t_defrost_ductcentral"] = 0.88

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 40379.49973723975)

    def test_入力値入替_04(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            デフロスト発生外気温度（ダクトセントラル空調機）
            defrost_temp_ductcentral
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["defrost_temp_ductcentral"] = 6.2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 41330.46136603447)

    def test_入力値入替_05(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            デフロスト発生外気相対湿度（ダクトセントラル空調機）
            defrost_humid_ductcentral
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["defrost_humid_ductcentral"] = 77

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 41565.19129722995)

    def test_入力値入替_06(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            ダクトiの線熱損失係数
            phi_i
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["phi_i"] = 0.52

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 14785.070861211718)
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 41236.578091305644)

    def test_入力値入替_07(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            暖房時の送風機の設計風量に関する係数
            C_V_fan_dsgn_H
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_V_fan_dsgn_H"] = 0.82

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 40775.15329048871)

    def test_入力値入替_08(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            冷房時の送風機の設計風量に関する係数
            C_V_fan_dsgn_C
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_V_fan_dsgn_C"] = 0.81

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 14788.362569150617)

    def test_入力値入替_09(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            デフロストに関する暖房出力補正係数（ルームエアコンディショナー）
            C_df_H_d_t_defrost_rac
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_df_H_d_t_defrost_rac"] = 0.88

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 40228.03332635408)

    def test_入力値入替_10(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            デフロスト発生外気温度（ルームエアコンディショナー）
            defrost_temp_rac
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["defrost_temp_rac"] = 5.2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 40925.918843796484)

    def test_入力値入替_11(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            デフロスト発生外気相対湿度（ルームエアコンディショナー）
            defrost_humid_rac
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["defrost_humid_rac"] = 82

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 40481.81864211065)

    def test_入力値入替_12(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            室内機吸い込み湿度に関する冷房出力補正係数
            C_hm_C
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_hm_C"] = 1.32

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 12824.79767377771)

    def test_入力値入替_13(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            定格冷房能力の最大値
            q_rtd_C_limit
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["q_rtd_C_limit"] = 3500

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 43487.16595274875)
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 17002.04875326623)

    def test_入力値入替_14(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            面積の合計 [m2]
            A_A
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["A_A"] = 135.92

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 40822.38807655774)
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 14184.472397667007)

    def test_入力値入替_15(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            主たる居室の面積 [m2]
            A_MR
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["A_MR"] = 68.29

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 47702.33872845253)
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 22378.09180122358)

    def test_入力値入替_16(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            その他の居室の面積[m2]
            A_OR
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["A_OR"] = 123.456

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 58567.764449747614)
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 25009.231072133218)

    def test_入力値入替_17(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            地域区分
            region
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["region"] = 1

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 174560.6036239345)
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 2884.2632006293015)

    def test_入力値入替_18(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            外皮面積 [m2]
            A_env
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["A_env"] = 333.332

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 45819.9093469388)
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 15119.878587850431)

    def test_入力値入替_19(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            外皮平均熱貫流率 UA [W/(m2・K)]
            U_A
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["U_A"] = 1.03

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 51145.64313095035)
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 14057.66109771598)

    def test_入力値入替_20(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            冷房期平均日射熱取得率ηAC
            eta_A_C
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["eta_A_C"] = 3.3

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 16690.55292080024)

    def test_入力値入替_21(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            暖房期平均日射熱取得率ηAH
            eta_A_H
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["eta_A_H"] = 3.9

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 43202.66151700742)

    def test_入力値入替_22(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            床下空間を経由して外気を導入する換気方式の利用 （☐：評価しない or ☑：評価する）
            underfloor_ventilation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["underfloor_ventilation"] = "2"

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 38306.56455225713)
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 12647.872661178222)

    def test_入力値入替_23(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            外気が経由する床下の面積の割合 [%]
            r_A_ufvnt
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫? 100 -> 85.0
        inputs["r_A_ufvnt"] = 85.0

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C == expected_result_type2.E_C

    def test_入力値入替_24(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            床下空間の断熱 （☐：断熱区画外 or ☑：断熱区画内）
            underfloor_insulation
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫? '1' -> '2'
        inputs["underfloor_insulation"] = '2'

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C == expected_result_type2.E_C

    def test_入力値入替_25(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            空調空気を床下を通して給気する （☐：床下を通して給気しない or ☑：床下を通して給気する）
            underfloor_air_conditioning_air_supply
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["underfloor_air_conditioning_air_supply"] = "2"

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 67493.42767621638)
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 18872.3162663047)

    def test_入力値入替_26(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            地盤またはそれを覆う基礎の表面熱伝達抵抗 [(m2・K)/W]
            R_g
        """
        inputs = copy.deepcopy(self._inputs)
        # WARNING: 値変更しても変わらないけど大丈夫? 0.15 -> 0.19
        inputs["R_g"] = 0.19

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C == expected_result_type2.E_C

    def test_入力値入替_27(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            全体風量を固定する （☐：固定しない or ☑：固定する）
            hs_CAV
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["hs_CAV"] = "2"

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 41606.24726343731)

    def test_入力値入替_H1(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            ダクトが通過する空間 （全てもしくは一部が断熱区画外である or 全て断熱区画内である）
            H_A_duct_insulation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["H_A"]["duct_insulation"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 38430.15407789486)

    def test_入力値入替_H2(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            VAV方式 （採用しない or 採用する）
            H_A_VAV
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["H_A"]["VAV"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 39572.83185804524)

    def test_入力値入替_H3(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            全般換気機能 （あり or なし）
            H_A_general_ventilation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["H_A"]["general_ventilation"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 41467.93507466678)

    def test_入力値入替_H4(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            設計風量 [m3/h]（入力する場合のみ）
            H_A_V_hs_dsgn_H
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["H_A"]["input_V_hs_dsgn_H"] = 2
        inputs["H_A"]["V_hs_dsgn_H"] = 1820

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 40896.18678654383)

    def test_入力値入替_H5_方式2(self, expected_inputs, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            暖房の機器仕様を入力する1
        """
        inputs = copy.deepcopy(self._inputs)

        # 暖房能力の入力（面積から能力を算出 or 性能を直接入力）
        inputs["H_A"]["input_rac_performance"] = 1  # ★ 面積から能力を算出
        # ▼ 入力する場合
        inputs["H_A"]["q_rac_rtd_H"] = 1  # 暖房定格能力 [W]
        inputs["H_A"]["q_rac_max_H"] = 1  # 暖房最大能力 [W]
        inputs["H_A"]["e_rac_rtd_H"] = 1  # 定格エネルギー効率 [-]

        # 小能力時高効率型コンプレッサー（評価しない or 搭載する）
        inputs["H_A"]["dualcompressor"] = 2

        # 設置方法の入力（設置方法を入力する or 補正係数を直接入力する）
        inputs["H_A"]["input_C_af_H"] = 1
        # ▼ 入力する場合
        inputs["H_A"]["C_af_H"] = 1  # 室内機吹き出し風量に関する暖房出力補正係数の入力

        # 専用チャンバーに格納される方式（該当しない or 該当する）
        inputs["H_A"]["dedicated_chamber"] = 2
        # フィン向きが中央位置に固定される方式（該当しない or 該当する）
        inputs["H_A"]["fixed_fin_direction"] = 2

        # ファンの比消費電力（入力しない or 入力する）
        inputs["H_A"]["input_f_SFP_H"] = 1
        # ▼ 入力する場合
        inputs["H_A"]["f_SFP_H"] = 1  # ファンの比消費電力 [W/(m3/h)]

        result = calc(inputs, test_mode=True)

        assert result['TInput'].q_max_H == expected_inputs.q_max_H
        assert result['TInput'].q_max_C == expected_inputs.q_max_C
        assert result['TInput'].q_rtd_H == expected_inputs.q_rtd_H
        assert result['TInput'].q_rtd_C == expected_inputs.q_rtd_C
        assert result['TInput'].e_rtd_H == expected_inputs.e_rtd_H
        assert result['TInput'].e_rtd_C == expected_inputs.e_rtd_C

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 31577.30541426199)

    def test_入力値入替_H6_方式2(self, expected_inputs, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            暖房の機器仕様を入力する2
        """
        inputs = copy.deepcopy(self._inputs)

        # 暖房能力の入力（面積から能力を算出 or 性能を直接入力）
        inputs["H_A"]["input_rac_performance"] = 2  # ★ 性能を直接入力
        # ▼ 入力する場合のみ
        inputs["H_A"]["q_rac_rtd_H"] = 3600  # 暖房定格能力 [W]
        inputs["H_A"]["q_rac_max_H"] = 4700  # 暖房最大能力 [W]
        inputs["H_A"]["e_rac_rtd_H"] = 3.93  # 定格エネルギー効率 [-]

        # 小能力時高効率型コンプレッサー（評価しない or 搭載する）
        inputs["H_A"]["dualcompressor"] = 1

        # 設置方法の入力（設置方法を入力する or 補正係数を直接入力する）
        inputs["H_A"]["input_C_af_H"] = 2  # ★ 補正係数を直接入力する
        # ▼ 入力する場合のみ
        inputs["H_A"]["C_af_H"] = 0.914  # 室内機吹き出し風量に関する暖房出力補正係数の入力

        # 専用チャンバーに格納される方式（該当しない or 該当する）
        inputs["H_A"]["dedicated_chamber"] = 1
        # フィン向きが中央位置に固定される方式（該当しない or 該当する）
        inputs["H_A"]["fixed_fin_direction"] = 1

        # ファンの比消費電力（入力しない or 入力する）
        inputs["H_A"]["input_f_SFP_H"] = 2  # ★ 入力する
        # ▼ 入力する場合のみ
        inputs["H_A"]["f_SFP_H"] = 0.3  # ファンの比消費電力 [W/(m3/h)]

        result = calc(inputs, test_mode=True)

        assert result['TInput'].q_max_C == expected_inputs.q_max_C
        assert result['TInput'].q_max_H != expected_inputs.q_max_H
        assert math.isclose(result['TInput'].q_max_H, 4700.0)

        assert result['TInput'].q_rtd_C == expected_inputs.q_rtd_C
        assert result['TInput'].q_rtd_H != expected_inputs.q_rtd_H
        assert math.isclose(result['TInput'].q_rtd_H, 3600.0)

        assert result['TInput'].e_rtd_C == expected_inputs.e_rtd_C
        assert result['TInput'].e_rtd_H != expected_inputs.e_rtd_H
        assert math.isclose(result['TInput'].e_rtd_H, 3.93)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 40540.29726496144)

    def test_入力値入替_R1(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            ダクトが通過する空間（全てもしくは一部が断熱区画外である or 全て断熱区画内である）
            C_A_duct_insulation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_A"]["duct_insulation"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 14407.53084233618)

    def test_入力値入替_R2(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            VAV方式 (採用しない or 採用する）
            C_A_VAV
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_A"]["VAV"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 12126.41287275799)

    def test_入力値入替_R3(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            全般換気機能（あり or なし）
            C_A_general_ventilation
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_A"]["general_ventilation"] = 2

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 15141.75913372107)

    def test_入力値入替_R4(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            設計風量 [m3/h]（入力する場合のみ）
            C_A_V_hs_dsgn_C
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["C_A"]["input_V_hs_dsgn_C"] = 2
        inputs["C_A"]["V_hs_dsgn_C"] = 1650

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 16296.897277400154)

    def test_入力値入替_R5_方式2(self, expected_result_type2, expected_inputs):
        """ 以前のプログラムと同じ計算結果になる
            冷房の機器仕様を入力する1
        """
        inputs = copy.deepcopy(self._inputs)

        # 冷房能力の入力（面積から能力を算出 or 性能を直接入力）
        inputs["C_A"]["input_rac_performance"] = 1  # ★ 面積から能力を算出
        # ▼ 入力する場合のみ
        inputs["C_A"]["q_rac_rtd_C"] = 1  # 冷房定格能力 [W]
        inputs["C_A"]["q_rac_max_C"] = 1  # 冷房最大能力 [W]
        inputs["C_A"]["e_rac_rtd_C"] = 1  # 定格エネルギー効率 [-]

        # 小能力時高効率型コンプレッサー（評価しない or 搭載する）
        inputs["C_A"]["dualcompressor"] = 2

        # 設置方法の入力（設置方法を入力する or 補正係数を直接入力する）
        inputs["C_A"]["input_C_af_C"] = 1  # ★ 設置方法を入力する
        # ▼ 入力する場合のみ
        inputs["C_A"]["C_af_C"] = 1  # 室内機吹き出し風量に関する暖房出力補正係数の入力

        # 専用チャンバーに格納される方式（該当しない or 該当する）
        inputs["C_A"]["dedicated_chamber"] = 2
        # フィン向きが中央位置に固定される方式（該当しない or 該当する）
        inputs["C_A"]["fixed_fin_direction"] = 2

        # ファンの比消費電力（入力しない or 入力する）
        inputs["C_A"]["input_f_SFP_C"] = 1  # ★ 入力しない
        # ▼ 入力する場合のみ
        inputs["C_A"]["f_SFP_C"] = 1  # ファンの比消費電力W [(m3/h)/W]

        result = calc(inputs, test_mode=True)

        assert result['TInput'].q_rtd_C == expected_inputs.q_rtd_C
        assert result['TInput'].q_rtd_H == expected_inputs.q_rtd_H
        assert result['TInput'].q_max_C == expected_inputs.q_max_C
        assert result['TInput'].q_max_H == expected_inputs.q_max_H
        assert result['TInput'].e_rtd_C == expected_inputs.e_rtd_C
        assert result['TInput'].e_rtd_H == expected_inputs.e_rtd_H

        assert result['TValue'].E_H == expected_result_type2.E_H
        assert result['TValue'].E_C != expected_result_type2.E_C
        assert math.isclose(result['TValue'].E_C, 14046.978599922277)

    def test_入力値入替_R6_方式2(self):
        """ 以前のプログラムと同じ計算結果になる
            冷房の機器仕様を入力する2
        """
        inputs = copy.deepcopy(self._inputs)

        # 冷房能力の入力（面積から能力を算出 or 性能を直接入力）
        inputs["C_A"]["input_rac_performance"] = 2  # ★ 面積から能力を算出
        # ▼ 入力する場合のみ
        inputs["C_A"]["q_rac_rtd_C"] = 2800  # 冷房定格能力 [W]
        inputs["C_A"]["q_rac_max_C"] = 3400  # 冷房最大能力 [W]
        inputs["C_A"]["e_rac_rtd_C"] = 2.59  # 定格エネルギー効率 [-]

        # 小能力時高効率型コンプレッサー（評価しない or 搭載する）
        inputs["C_A"]["dualcompressor"] = 1

        # 設置方法の入力（設置方法を入力する or 補正係数を直接入力する）
        inputs["C_A"]["input_C_af_C"] = 2  # ★ 補正係数を直接入力する
        # ▼ 入力する場合のみ
        inputs["C_A"]["C_af_C"] = 0.980  # 室内機吹き出し風量に関する冷房出力補正係数の入力

        # 専用チャンバーに格納される方式（該当しない or 該当する）
        inputs["C_A"]["dedicated_chamber"] = 1
        # フィン向きが中央位置に固定される方式（該当しない or 該当する）
        inputs["C_A"]["fixed_fin_direction"] = 1

        # ファンの比消費電力（入力しない or 入力する）
        inputs["C_A"]["input_f_SFP_C"] = 2  # ★ 入力する
        # ▼ 入力する場合のみ
        inputs["C_A"]["f_SFP_C"] = 0.3  # ファンの比消費電力W [(m3/h)/W]

        result = calc(inputs, test_mode=True)

        # TODO: 暖房についても結果が変わるのは大丈夫?
        assert math.isclose(result['TInput'].q_rtd_C, 2800.0)
        assert math.isclose(result['TInput'].q_rtd_H, 3300.1000000000004)
        assert math.isclose(result['TInput'].q_max_C, 3400.0)
        assert math.isclose(result['TInput'].q_max_H, 5569.280000000001)
        assert math.isclose(result['TInput'].e_rtd_C, 2.59)
        assert math.isclose(result['TInput'].e_rtd_H, 3.6543)

        assert math.isclose(result['TValue'].E_C, 21336.043883848488)
        assert math.isclose(result['TValue'].E_H, 46940.16551587674)

    def test_入力値入替_HEX1(self, expected_result_type2):
        """ 以前のプログラムと同じ計算結果になる
            温度交換効率（設置する場合のみ）
            etr_t
        """
        inputs = copy.deepcopy(self._inputs)
        inputs["HEX"]["install"] = 2
        inputs["HEX"]["etr_t"] = 0.3

        result = calc(inputs, test_mode=True)

        assert result['TValue'].E_C == expected_result_type2.E_C
        assert result['TValue'].E_H != expected_result_type2.E_H
        assert math.isclose(result['TValue'].E_H, 38022.75810040755)
