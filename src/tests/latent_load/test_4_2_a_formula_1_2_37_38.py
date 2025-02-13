import json
import numpy as np

from pyhees.section3_2 import calc_r_env
import pyhees.section4_1 as H
import pyhees.section4_2_a as dc_a

# JJJ
import jjjexperiment.input as input
import jjjexperiment.constants as constants
from jjjexperiment.constants import PROCESS_TYPE_1, PROCESS_TYPE_2, PROCESS_TYPE_3
import jjjexperiment.section4_2 as jjj_dc
import jjjexperiment.section4_2_a as jjj_dc_a
from jjjexperiment.logger import LimitedLoggerAdapter as _logger
# JJJ-test
from test_utils.utils import INPUT_SAMPLE_TYPE3_PATH

# 潜熱評価モデルのテストコード

def prepare_args_for_calc_Q_UT_A() -> dict:
    inputs = json.load(open(INPUT_SAMPLE_TYPE3_PATH, 'r'))

    inputs["H_A"]["input_V_hs_dsgn_H"] = 2  # ユーザー入力ON
    inputs["C_A"]["input_V_hs_dsgn_C"] = 2  # ユーザー入力ON
    constants.set_constants(inputs)

    # 個別の変数に展開
    _, _, A_A, A_MR, A_OR, region, sol_region = input.get_basic(inputs)
    ENV, NV_MR, NV_OR, TS, r_A_ufvnt, uflr_insul, uflr_air_cdtn_air_spl, hs_CAV = input.get_env(inputs)
    mode_H, H_A, _, _, _  = input.get_heating(inputs, region, A_A)
    mode_C, C_A, _, _     = input.get_cooling(inputs, region, A_A)
    q_rtd_C, q_rtd_H, q_max_C, q_max_H, e_rtd_C, e_rtd_H, dualcompressor_C, dualcompressor_H, input_C_af_C, input_C_af_H \
        = input.get_CRAC_spec(inputs)

    # 設計風量[m3/h]
    V_hs_dsgn_H, V_hs_dsgn_C = H_A['V_hs_dsgn_H'], C_A['V_hs_dsgn_C']  # NOTE: ユーザー入力ON時のみ可

    fixtures = {
        "case_name": "-",
        "climateFile": "-",
        "loadFile": "-",
        "Q": 2.647962191872085,
        "mu_C": 0.07170453031312457,
        "mu_H": 0.11011767155229846,
        "YUCACO_r_A_ufvnt": 0.7089130102430821,
        "HEX": None,
        "SHC": None,
        "R_g": None,
        "spec_MR": None,
        "spec_OR": None,
        "mode_MR": None,
        "mode_OR": None,
    }

    L_H_d_t_i: np.ndarray  # H: 暖房負荷 [MJ/h]
    L_H_d_t_i, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i = H.calc_heating_load(
        region = region,
        sol_region = sol_region,
        A_A = A_A, A_MR = A_MR, A_OR = A_OR,
        NV_MR = NV_MR, NV_OR = NV_OR, TS = TS,
        r_A_ufvnt = r_A_ufvnt,
        underfloor_insulation = uflr_insul,
        mode_H = mode_H, mode_C = mode_C,
        Q =    fixtures["Q"],
        mu_H = fixtures["mu_H"],
        mu_C = fixtures["mu_C"],
        spec_MR = fixtures["spec_MR"],
        spec_OR = fixtures["spec_OR"],
        mode_MR = fixtures["mode_MR"],
        mode_OR = fixtures["mode_OR"],
        HEX = fixtures["HEX"],
        SHC = fixtures["SHC"])

    L_CS_d_t_i: np.ndarray  # CS: 冷房・顕熱負荷 [MJ/h]
    L_CL_d_t_i: np.ndarray  # CL: 冷房・潜熱負荷 [MJ/h]
    L_CS_d_t_i, L_CL_d_t_i = H.calc_cooling_load(
        region = region,
        A_A = A_A, A_MR = A_MR, A_OR = A_OR,
        NV_MR = NV_MR, NV_OR = NV_OR, TS = TS,
        r_A_ufvnt = r_A_ufvnt,
        underfloor_insulation = uflr_insul,
        mode_C = mode_C, mode_H = mode_H,
        Q =    fixtures["Q"],
        mu_H = fixtures["mu_H"],
        mu_C = fixtures["mu_C"],
        mode_MR = fixtures["mode_MR"],
        mode_OR = fixtures["mode_OR"],
        HEX =     fixtures["HEX"])

    r_env = calc_r_env(
        method='当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法',
        A_env=ENV['A_env'],
        A_A=A_A
    )

    main_args = {
        'case_name': fixtures['case_name'],
        'A_A': A_A,
        'A_MR': A_MR,
        'A_OR': A_OR,
        'r_env': r_env,  # A_env から変更
        'mu_H': fixtures["mu_H"],
        'mu_C': fixtures["mu_C"],
        'q_rtd_H': q_rtd_H,
        'q_rtd_C': q_rtd_C,
        'q_max_H': q_max_H,
        'q_max_C': q_max_C,
        'Q': fixtures["Q"],
        'hs_CAV': hs_CAV,
        'region': region,
        'L_H_d_t_i': L_H_d_t_i,
        'L_CS_d_t_i': L_CS_d_t_i,
        'L_CL_d_t_i': L_CL_d_t_i,
        'input_C_af_H': input_C_af_H,
        'input_C_af_C': input_C_af_C,
        'underfloor_insulation': uflr_insul,
        'underfloor_air_conditioning_air_supply': uflr_air_cdtn_air_spl,
        'YUCACO_r_A_ufvnt': fixtures["YUCACO_r_A_ufvnt"],
        # 'R_g': fixtures["R_g"],
        'climateFile': fixtures["climateFile"],
        'L_dash_H_R_d_t_i': L_dash_H_R_d_t_i,
        'L_dash_CS_R_d_t_i': L_dash_CS_R_d_t_i,
        'r_A_ufvnt': r_A_ufvnt
    }
    H_args = {
        'VAV': H_A['VAV'],
        'general_ventilation': H_A['general_ventilation'],
        'duct_insulation': H_A['duct_insulation'],
        'type': H_A['type'],
        'q_hs_rtd_H': H_A['q_hs_rtd_H'],
        "q_hs_rtd_C": C_A['q_hs_rtd_C'],  # NOTE: 後に None で上書きするが必要
        'V_hs_dsgn_H': V_hs_dsgn_H,
        'V_hs_dsgn_C': None,  # NOTE: 暖房時除外項目
    }
    C_args = {
        'VAV': C_A['VAV'],
        'general_ventilation': C_A['general_ventilation'],
        'duct_insulation': C_A['duct_insulation'],
        'type': C_A['type'],
        'q_hs_rtd_H': H_A['q_hs_rtd_H'],  # NOTE: 後に None で上書きするが必要
        "q_hs_rtd_C": C_A['q_hs_rtd_C'],
        'V_hs_dsgn_H': None,  # NOTE: 冷房時除外項目
        'V_hs_dsgn_C': V_hs_dsgn_C,
    }
    others = {
        'q_hs_min_H':  H_A['q_hs_min_H'],
        'q_hs_min_C':  C_A['q_hs_min_C'],
        'q_hs_mid_H':  H_A['q_hs_mid_H'],
        "q_hs_mid_C":  C_A['q_hs_mid_C'],
        'P_hs_mid_H':  H_A['P_hs_mid_H'],
        "P_hs_mid_C":  C_A['P_hs_mid_C'],
        'V_fan_mid_H': H_A['V_fan_mid_H'],
        "V_fan_mid_C": C_A['V_fan_mid_C'],
        'P_fan_mid_H': H_A['P_fan_mid_H'],
        "P_fan_mid_C": C_A['P_fan_mid_C'],
        'V_fan_rtd_H': H_A['V_fan_rtd_H'],
        "V_fan_rtd_C": C_A['V_fan_rtd_C'],
        'e_rtd_H': e_rtd_H,
        "e_rtd_C": e_rtd_C,
        'P_fan_rtd_H': H_A['P_fan_rtd_H'],
        "P_fan_rtd_C": C_A['P_fan_rtd_C'],
        'P_hs_rtd_H': H_A['P_hs_rtd_H'],
        "P_hs_rtd_C": C_A['P_hs_rtd_C'],
        'dualcompressor_H': dualcompressor_H,
        "dualcompressor_C": dualcompressor_C,
        'EquipmentSpec_H': H_A['EquipmentSpec'],
        "EquipmentSpec_C": C_A['EquipmentSpec'],
        'f_SFP_H': H_A['f_SFP_H'],
        "f_SFP_C": C_A['f_SFP_C'],
    }
    return main_args, H_args, C_args, others


class Testファン消費電力_暖房:

    def prepareArgs(self) -> None:
        """ 暖房用のセットアップ
        """
        main_args, H_args, _, others = prepare_args_for_calc_Q_UT_A()
        H_args['q_hs_rtd_C'] = None  # NOTE: 暖房負荷の計算時には冷房の定格出力は無視する
        main_args.update(H_args)

        _, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, _, _, _, V_hs_supply_d_t, V_hs_vent_d_t, V_vent_g_i, C_df_H_d_t \
            = jjj_dc.calc_Q_UT_A(**main_args)

        q_hs_H_d_t = dc_a.get_q_hs_H_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, V_hs_supply_d_t, C_df_H_d_t, main_args['region'])

        self._testEEfanArgs = {
            'type': H_args['type'],
            'region': main_args['region'],
            'case_name': main_args['case_name'],
            'input_V_hs_min': constants.input_V_hs_min,
            'general_ventilation': H_args['general_ventilation'],
            'V_vent_g_i': V_vent_g_i,
            'Theta_hs_out_d_t': Theta_hs_out_d_t,
            'Theta_hs_in_d_t': Theta_hs_in_d_t,
            'V_hs_supply_d_t': V_hs_supply_d_t,
            'V_hs_vent_d_t': V_hs_vent_d_t,
            'V_hs_dsgn_H': H_args['V_hs_dsgn_H'],
            'C_df_H_d_t': C_df_H_d_t,
            'P_rac_fan_rtd_H': others['P_fan_rtd_H'],
            'P_fan_rtd_H': others['P_fan_rtd_H'],
            'f_SFP_H': others['f_SFP_H'],
        }

    _testEEfanArgs: dict

    @classmethod
    def setup_class(cls):
        """ 暖房方式 以外の引数は共通として、方式ごとの挙動差のみを確認する
        """
        cls.prepareArgs(cls)

    def test_方式1_方式2_結果一致(self):
        self._testEEfanArgs['type'] = PROCESS_TYPE_1
        result_01, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        self._testEEfanArgs['type'] = PROCESS_TYPE_2
        result_02, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        assert np.all(result_01 == result_02)

    def test_方式1_方式3_計算切替(self):
        self._testEEfanArgs['type'] = PROCESS_TYPE_1
        result_01, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        self._testEEfanArgs['type'] = PROCESS_TYPE_3
        result_03, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        assert not np.all(result_01 == result_03)

    def test_方式2_方式3_計算切替(self):
        self._testEEfanArgs['type'] = PROCESS_TYPE_2
        result_02, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        self._testEEfanArgs['type'] = PROCESS_TYPE_3
        result_03, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        assert not np.all(result_02 == result_03)

    def test_方式3_係数設定_変更反映(self):
        """ 同じ方式3でもユーザーが設定した係数によって計算結果が異なることを確認
        """
        self._testEEfanArgs['type'] = PROCESS_TYPE_3
        update_info_01 = {
            'H_A': {'fan_coeff': [0, 0, 27, -8, 13]}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_01)
        result_03_01, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        update_info_02 = {
            'H_A': {'fan_coeff': [0, 0, 13, 20, -6]}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_02)
        result_03_02, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)

        assert not np.all(result_03_01 == result_03_02)


class Testファン消費電力_冷房:

    def prepareArgs(self) -> None:
        """ 冷房用のセットアップ
        """
        main_args, _, C_args, others = prepare_args_for_calc_Q_UT_A()
        C_args['q_hs_rtd_H'] = None  # NOTE: 冷房負荷の計算時には暖房の定格出力は無視する
        main_args.update(C_args)

        _, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, _, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, V_hs_vent_d_t, V_vent_g_i, _ \
            = jjj_dc.calc_Q_UT_A(**main_args)

        q_hs_C_d_t = dc_a.get_q_hs_C_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, main_args['region'])

        self._testEEfanArgs = {
            'type': C_args['type'],
            'region': main_args['region'],
            'case_name': main_args['case_name'],
            'input_V_hs_min': constants.input_V_hs_min,
            'general_ventilation': C_args['general_ventilation'],
            'V_vent_g_i': V_vent_g_i,
            'Theta_hs_out_d_t': Theta_hs_out_d_t,
            'Theta_hs_in_d_t': Theta_hs_in_d_t,
            'V_hs_supply_d_t': V_hs_supply_d_t,
            'V_hs_vent_d_t': V_hs_vent_d_t,
            'V_hs_dsgn_C': C_args['V_hs_dsgn_C'],
            'X_hs_out_d_t': X_hs_out_d_t,
            'X_hs_in_d_t': X_hs_in_d_t,
            'P_rac_fan_rtd_C': others['P_fan_rtd_C'],
            'P_fan_rtd_C': others['P_fan_rtd_C'],
            'f_SFP_C': others['f_SFP_C'],
        }

    _testEEfanArgs: dict

    @classmethod
    def setup_class(cls):
        """ 冷房方式 以外の引数は共通として、方式ごとの挙動差のみを確認する
        """
        cls.prepareArgs(cls)

    def test_方式1_方式2_結果一致(self):
        self._testEEfanArgs['type'] = PROCESS_TYPE_1
        result_01, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testEEfanArgs['type'] = PROCESS_TYPE_2
        result_02, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        assert np.all(result_01 == result_02)

    def test_方式1_方式3_計算切替(self):
        self._testEEfanArgs['type'] = PROCESS_TYPE_1
        result_01, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testEEfanArgs['type'] = PROCESS_TYPE_3
        result_03, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        assert not np.all(result_01 == result_03)

    def test_方式2_方式3_計算切替(self):
        self._testEEfanArgs['type'] = PROCESS_TYPE_2
        result_02, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testEEfanArgs['type'] = PROCESS_TYPE_3
        result_03, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        assert not np.all(result_02 == result_03)

    def test_方式3_係数設定_変更反映(self):
        """ 同じ方式3でもユーザーが設定した係数によって計算結果が異なることを確認
        """
        self._testEEfanArgs['type'] = PROCESS_TYPE_3
        update_info_01 = {
            'C_A': {'fan_coeff': [0, 0, 27, -8, 13]}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_01)
        result_03_01, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)

        update_info_02 = {
            'C_A': {'fan_coeff': [0, 0, 13, 20, -6]}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_02)
        result_03_02, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)

        assert not np.all(result_03_01 == result_03_02)


class Testコンプレッサ効率特性_暖房:

    def prepareArgs(self) -> None:
        """ 暖房用のセットアップ
        """
        main_args, H_args, _, others = prepare_args_for_calc_Q_UT_A()
        q_hs_rtd_C = H_args['q_hs_rtd_C']
        H_args['q_hs_rtd_C'] = None  # NOTE: 暖房負荷の計算時には冷房の定格出力は無視する
        main_args.update(H_args)

        _, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t, _, _, V_hs_supply_d_t, V_hs_vent_d_t, V_vent_g_i, C_df_H_d_t \
            = jjj_dc.calc_Q_UT_A(**main_args)

        # 送風機の消費電力[W] = 設計風量[m3/h] * 比消費電力[W/(m3/h)]
        P_rac_fan_rtd_H = H_args['V_hs_dsgn_H'] * others['f_SFP_H']

        # NOTE: calc_E_E_H_d_t_type1_and_type3 の引数と一致
        self._testBaseArgs = {
            'type': H_args['type'],
            'E_E_fan_H_d_t': None,  # TODO: 最適な初期化
            'q_hs_H_d_t': None,  # TODO: 最適な初期化
            'Theta_hs_out_d_t': Theta_hs_out_d_t,
            'Theta_hs_in_d_t': Theta_hs_in_d_t,
            'Theta_ex_d_t': Theta_ex_d_t,
            'V_hs_supply_d_t': V_hs_supply_d_t,
            'q_hs_rtd_C': q_hs_rtd_C,
            'q_hs_min_H': others['q_hs_min_H'],
            'q_hs_mid_H': others['q_hs_mid_H'],
            'P_hs_mid_H': others['P_hs_mid_H'],
            'V_fan_mid_H': others['V_fan_mid_H'],
            'P_fan_mid_H': others['P_fan_mid_H'],
            'q_hs_rtd_H': H_args['q_hs_rtd_H'],
            'P_fan_rtd_H': others['P_fan_rtd_H'],
            'V_fan_rtd_H': others['V_fan_rtd_H'],
            'P_hs_rtd_H': others['P_hs_rtd_H'],
            'EquipmentSpec': others['EquipmentSpec_H']
        }

        # NOTE: calc_E_E_H_d_t_type2 の引数と一致
        self._testBaseArgs2 = {
            'type': H_args['type'],
            'region': main_args['region'],
            'climateFile': main_args['climateFile'],
            'E_E_fan_H_d_t': None,  # TODO: 最適な初期化
            'q_hs_H_d_t': None,  # TODO: 最適な初期化
            'e_rtd_H': others['e_rtd_H'],
            'q_rtd_H': main_args['q_rtd_H'],
            'q_rtd_C': main_args['q_rtd_C'],
            'q_max_H': main_args['q_max_H'],
            'q_max_C': main_args['q_max_C'],
            'input_C_af_H': main_args['input_C_af_H'],
            'dualcompressor_H': others['dualcompressor_H'],
        }

        # NOTE: calc_E_E_fun_H_d_t の引数と一致
        self._testEEfanArgs = {
            'type': H_args['type'],
            'region': main_args['region'],
            'case_name': "Test",
            'input_V_hs_min': constants.input_V_hs_min,
            'general_ventilation': H_args['general_ventilation'],
            'V_vent_g_i': V_vent_g_i,
            'Theta_hs_out_d_t': Theta_hs_out_d_t,
            'Theta_hs_in_d_t': Theta_hs_in_d_t,
            'V_hs_supply_d_t': V_hs_supply_d_t,
            'V_hs_vent_d_t': V_hs_vent_d_t,
            'V_hs_dsgn_H': H_args['V_hs_dsgn_H'],
            'C_df_H_d_t': C_df_H_d_t,
            'P_rac_fan_rtd_H': P_rac_fan_rtd_H,
            'P_fan_rtd_H': others['P_fan_rtd_H'],
            'f_SFP_H': others['f_SFP_H']
        }

    _testBaseArgs: dict
    """type1, type3"""
    _testBaseArgs2: dict
    """type2"""
    _testEEfanArgs: dict
    """E_E_fan計算用の関数はタイプ共通"""

    @classmethod
    def setup_class(cls):
        """ 暖房方式 以外の引数は共通として、方式ごとの挙動差のみを確認する
        """
        cls.prepareArgs(cls)

    def test_時間別消費電力量_方式1_方式3_送風機不変(self):

        self._testEEfanArgs["type"] = PROCESS_TYPE_1
        E_E_fan_H_d_t1, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)

        self._testEEfanArgs["type"] = PROCESS_TYPE_3
        E_E_fan_H_d_t3, _ = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)

        # TODO: (5) ファン消費電力 の実装によって変更があるが仕様通りがチェック
        assert not np.array_equal(E_E_fan_H_d_t1, E_E_fan_H_d_t3), "送風機分の消費電力には方式による差が生じるはずです"

    def test_時間別消費電力量_方式1_方式3_合計値変化(self):

        self._testEEfanArgs['type'] = PROCESS_TYPE_1
        E_E_fan_H_d_t1, q_hs_H_d_t1 = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_1
        self._testBaseArgs['E_E_fan_H_d_t'] = E_E_fan_H_d_t1
        self._testBaseArgs['q_hs_H_d_t'] = q_hs_H_d_t1
        E_E_H_d_t1 = jjj_dc_a.calc_E_E_H_d_t_type1_and_type3(**self._testBaseArgs)

        self._testEEfanArgs['type'] = PROCESS_TYPE_3
        E_E_fan_H_d_t3, q_hs_H_d_t3 = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_3
        self._testBaseArgs['E_E_fan_H_d_t'] = E_E_fan_H_d_t3
        self._testBaseArgs['q_hs_H_d_t'] = q_hs_H_d_t3
        E_E_H_d_t3 = jjj_dc_a.calc_E_E_H_d_t_type1_and_type3(**self._testBaseArgs)

        assert not np.array_equal(E_E_H_d_t1, E_E_H_d_t3), "方式によって消費電力の計算値には差が生じなければなりません"

    def test_時間別消費電力量_方式1_方式2_両方変化(self):

        self._testEEfanArgs['type'] = PROCESS_TYPE_1
        E_E_fan_H_d_t1, q_hs_H_d_t1 = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_1
        self._testBaseArgs['E_E_fan_H_d_t'] = E_E_fan_H_d_t1
        self._testBaseArgs['q_hs_H_d_t'] = q_hs_H_d_t1
        E_E_H_d_t1 = jjj_dc_a.calc_E_E_H_d_t_type1_and_type3(**self._testBaseArgs)

        self._testEEfanArgs['type'] = PROCESS_TYPE_2
        E_E_fan_H_d_t2, q_hs_H_d_t2 = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        self._testBaseArgs2['type'] = PROCESS_TYPE_2
        self._testBaseArgs2['E_E_fan_H_d_t'] = E_E_fan_H_d_t2
        self._testBaseArgs2['q_hs_H_d_t'] = q_hs_H_d_t2
        E_E_H_d_t2 = jjj_dc_a.calc_E_E_H_d_t_type2(**self._testBaseArgs2)

        assert np.array_equal(E_E_fan_H_d_t1, E_E_fan_H_d_t2), "誤って送風機分の消費電力にも方式による差が生じています"
        assert not np.array_equal(E_E_H_d_t1, E_E_H_d_t2), "方式によって消費電力の計算値には差が生じなければなりません"

    def test_時間別消費電力量_方式3_係数設定有効(self):
        """ コンプレッサ効率特性曲線のパラメータ設定が結果に反映されていることを確認
        """
        self._testEEfanArgs['type'] = PROCESS_TYPE_3
        # コンプレッサ効率特性 係数は Type3 でのみ有効
        coeffs_01 = [0, 0, -0.444, 0.444, 0]
        coeffs_02 = [0, 0.153, -0.53, 0.53, 0]

        update_info_01 = {
            'H_A': {'compressor_coeff': coeffs_01}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_01)
        E_E_fan_H_d_t3_1, q_hs_H_d_t3_1 = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_3
        self._testBaseArgs['E_E_fan_H_d_t'] = E_E_fan_H_d_t3_1
        self._testBaseArgs['q_hs_H_d_t'] = q_hs_H_d_t3_1
        E_E_H_d_t3_1 = jjj_dc_a.calc_E_E_H_d_t_type1_and_type3(**self._testBaseArgs)

        update_info_02 = {
            'H_A': {'compressor_coeff': coeffs_02}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_02)
        E_E_fan_H_d_t3_2, q_hs_H_d_t3_2 = jjj_dc_a.calc_E_E_fan_H_d_t(**self._testEEfanArgs)
        self._testBaseArgs['type'] = PROCESS_TYPE_3
        self._testBaseArgs['E_E_fan_H_d_t'] = E_E_fan_H_d_t3_2
        self._testBaseArgs['q_hs_H_d_t'] = q_hs_H_d_t3_2
        E_E_H_d_t3_2 = jjj_dc_a.calc_E_E_H_d_t_type1_and_type3(**self._testBaseArgs)

        assert np.array_equal(E_E_fan_H_d_t3_1, E_E_fan_H_d_t3_1), "誤って送風機分の消費電力にも方式による差が生じています"
        assert not np.array_equal(E_E_H_d_t3_1, E_E_H_d_t3_2), "コンプレッサ効率特性曲線の係数が結果に反映されていません"

class Testコンプレッサ効率特性_冷房:

    def prepareArgs(self) -> None:
        """ 冷房用のセットアップ
        """
        main_args, _, C_args, others = prepare_args_for_calc_Q_UT_A()
        q_hs_rtd_H = C_args['q_hs_rtd_H']  # NOTE: 暖房と異なる点で使用しない
        C_args['q_hs_rtd_H'] = None  # NOTE: 冷房負荷の計算時には暖房の定格出力は無視する
        main_args.update(C_args)

        _, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, Theta_ex_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, V_hs_vent_d_t, V_vent_g_i, _ \
            = jjj_dc.calc_Q_UT_A(**main_args)

        # 送風機の消費電力[W] = 設計風量[m3/h] * 比消費電力[W/(m3/h)]
        P_rac_fan_rtd_C = C_args['V_hs_dsgn_C'] * others['f_SFP_C']

        # NOTE: calc_E_E_fan_C_d_t の引数に対応
        self._testEEfanArgs = {
            "type": C_args['type'],
            "region": main_args['region'],
            "case_name": "Test",
            "input_V_hs_min": False,  # TODO: 最適な初期化
            "general_ventilation": C_args['general_ventilation'],
            "V_vent_g_i": V_vent_g_i,
            "Theta_hs_out_d_t": Theta_hs_out_d_t,
            "Theta_hs_in_d_t": Theta_hs_in_d_t,
            "V_hs_supply_d_t": V_hs_supply_d_t,
            "V_hs_vent_d_t": V_hs_vent_d_t,
            "V_hs_dsgn_C": C_args['V_hs_dsgn_C'],
            "X_hs_out_d_t": X_hs_out_d_t,
            "X_hs_in_d_t": X_hs_in_d_t,
            "P_rac_fan_rtd_C": P_rac_fan_rtd_C,
            "P_fan_rtd_C": others['P_fan_rtd_C'],
            "f_SFP_C": others['f_SFP_C']
        }

        # NOTE: calc_E_E_C_d_t_type1_and_type3 の引数に対応
        self._testBaseArgs = {
            "type": C_args['type'],
            "region": main_args['region'],
            "E_E_fan_C_d_t": None,  # TODO: 最適な初期化
            "Theta_hs_out_d_t": Theta_hs_out_d_t,
            "Theta_hs_in_d_t": Theta_hs_in_d_t,
            "Theta_ex_d_t": Theta_ex_d_t,
            "V_hs_supply_d_t": V_hs_supply_d_t,
            "X_hs_out_d_t": X_hs_out_d_t,
            "X_hs_in_d_t": X_hs_in_d_t,
            "q_hs_min_C": others['q_hs_min_C'],
            "q_hs_mid_C": others['q_hs_mid_C'],
            "P_hs_mid_C": others['P_hs_mid_C'],
            "V_fan_mid_C": others['V_fan_mid_C'],
            "P_fan_mid_C": others['P_fan_mid_C'],
            "q_hs_rtd_C": C_args['q_hs_rtd_C'],  # NOTE: 冷房時であっても必要
            "P_fan_rtd_C": others['P_fan_rtd_C'],
            "V_fan_rtd_C": others['V_fan_rtd_C'],
            "P_hs_rtd_C": others['P_hs_rtd_C'],
            "EquipmentSpec": others['EquipmentSpec_C'],
        }

        # NOTE: calc_E_E_C_d_t_type2 の引数に対応
        self._testBaseArgs2 = {
            "type": C_args['type'],
            "region": main_args['region'],
            "climateFile": main_args['climateFile'],
            "E_E_fan_C_d_t": None,
            "q_hs_CS_d_t": None,
            "q_hs_CL_d_t": None,
            "e_rtd_C": others['e_rtd_C'],
            "q_rtd_C": main_args['q_rtd_C'],
            "q_max_C": main_args['q_max_C'],
            "input_C_af_C":  main_args['input_C_af_C'],
            "dualcompressor_C": others['dualcompressor_C'],
        }

    _testBaseArgs: dict
    """type1, type3"""
    _testBaseArgs2: dict
    """type2"""
    _testEEfanArgs: dict
    """E_E_fan計算用の関数はタイプ共通"""

    @classmethod
    def setup_class(cls):
        """ 冷房方式 以外の引数は共通として、方式ごとの挙動差のみを確認する
        """
        cls.prepareArgs(cls)

    def test_時間別消費電力量_方式1_方式3_送風機不変(self):

        self._testEEfanArgs["type"] = PROCESS_TYPE_1
        E_E_fan_C_d_t_T1, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testEEfanArgs["type"] = PROCESS_TYPE_3
        E_E_fan_C_d_t_T3, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)

        # TODO: (5) ファン消費電力 の実装によって変更があるが仕様通りがチェック
        assert not np.array_equal(E_E_fan_C_d_t_T1, E_E_fan_C_d_t_T3), "送風機分の消費電力には方式による差が生じるはずです"

    def test_時間別消費電力量_方式1_方式3_平均冷房能力不変(self):

        self._testEEfanArgs["type"] = PROCESS_TYPE_1
        _, q_hs_CS_d_t_T1, q_hs_CL_d_t_T1 = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testEEfanArgs["type"] = PROCESS_TYPE_3
        _, q_hs_CS_d_t_T3, q_hs_CL_d_t_T3 = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)

        assert np.array_equal(q_hs_CS_d_t_T1, q_hs_CS_d_t_T3), "誤って平均冷房顕熱能力にも方式による差が生じています"
        assert np.array_equal(q_hs_CL_d_t_T1, q_hs_CL_d_t_T3), "誤って平均冷房潜熱能力にも方式による差が生じています"

    def test_時間別消費電力量_方式1_方式3_合計値変化(self):

        self._testEEfanArgs["type"] = PROCESS_TYPE_1
        E_E_fan_C_d_t_T1, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testBaseArgs["E_E_fan_C_d_t"] = E_E_fan_C_d_t_T1
        E_E_C_d_t_T1 = jjj_dc_a.calc_E_E_C_d_t_type1_and_type3(**self._testBaseArgs)

        self._testEEfanArgs["type"] = PROCESS_TYPE_3
        E_E_fan_C_d_t_T3, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testBaseArgs["E_E_fan_C_d_t"] = E_E_fan_C_d_t_T3
        E_E_C_d_t_T3 = jjj_dc_a.calc_E_E_C_d_t_type1_and_type3(**self._testBaseArgs)

        assert not np.array_equal(E_E_C_d_t_T1, E_E_C_d_t_T3), "方式によって消費電力の計算値には差が生じなければなりません"

    def test_時間別消費電力量_方式1_方式2_両方変化(self):

        self._testEEfanArgs["type"] = PROCESS_TYPE_1
        E_E_fan_C_d_t_T1, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testBaseArgs["E_E_fan_C_d_t"] = E_E_fan_C_d_t_T1
        E_E_C_d_t_T1 = jjj_dc_a.calc_E_E_C_d_t_type1_and_type3(**self._testBaseArgs)

        self._testEEfanArgs["type"] = PROCESS_TYPE_2
        E_E_fan_C_d_t_T2, q_hs_CS_d_t, q_hs_CL_d_t = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testBaseArgs2["type"] = PROCESS_TYPE_2
        self._testBaseArgs2["E_E_fan_C_d_t"] = E_E_fan_C_d_t_T2
        self._testBaseArgs2["q_hs_CS_d_t"] = q_hs_CS_d_t
        self._testBaseArgs2["q_hs_CL_d_t"] = q_hs_CL_d_t
        E_E_C_d_t_T2  = jjj_dc_a.calc_E_E_C_d_t_type2(**self._testBaseArgs2)

        assert np.array_equal(E_E_fan_C_d_t_T1, E_E_fan_C_d_t_T2), "誤って送風機分の消費電力にも方式による差が生じています"
        assert not np.array_equal(E_E_C_d_t_T1, E_E_C_d_t_T2), "方式によって消費電力の計算値には差が生じなければなりません"

    def test_時間別消費電力量_方式3_係数設定有効(self):
        """ コンプレッサ効率特性曲線のパラメータ設定が結果に反映されていることを確認
        """
        self._testEEfanArgs["type"] = PROCESS_TYPE_3
        # コンプレッサ効率特性 係数は Type3 でのみ有効
        coeffs_01 = [0, 0, -0.444, 0.444, 0]
        coeffs_02 = [0, 0.153, -0.53, 0.53, 0]

        update_info_01 = {
            'C_A': {'compressor_coeff': coeffs_01}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_01)
        E_E_fan_C_d_t_T301, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testBaseArgs["type"] = PROCESS_TYPE_3
        self._testBaseArgs["E_E_fan_C_d_t"] = E_E_fan_C_d_t_T301
        E_E_C_d_t_T301 = jjj_dc_a.calc_E_E_C_d_t_type1_and_type3(**self._testBaseArgs)

        update_info_02 = {
            'C_A': {'compressor_coeff': coeffs_02}  # NOTE: ユーザーの独自値で設定
        }
        constants.set_constants(update_info_02)
        E_E_fan_C_d_t_T302, _, _ = jjj_dc_a.calc_E_E_fan_C_d_t(**self._testEEfanArgs)
        self._testBaseArgs["E_E_fan_C_d_t"] = E_E_fan_C_d_t_T302
        E_E_C_d_t_T302 = jjj_dc_a.calc_E_E_C_d_t_type1_and_type3(**self._testBaseArgs)

        assert not np.array_equal(E_E_C_d_t_T301, E_E_C_d_t_T302), "コンプレッサ効率特性曲線の係数が結果に反映されていません"
        assert np.array_equal(E_E_fan_C_d_t_T301, E_E_fan_C_d_t_T302), "誤って送風機分の消費電力にも方式による差が生じています"
