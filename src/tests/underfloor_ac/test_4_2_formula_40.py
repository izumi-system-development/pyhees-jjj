import os
import numpy as np
import pyhees.section3_1 as ld
import pyhees.section3_1_d as uf
import pyhees.section3_1_e as algo
import pyhees.section4_1 as H
import pyhees.section4_2 as dc

# JJJ
from jjjexperiment.input import get_solarheat
import jjjexperiment.inputs as jjj_ipt
import jjjexperiment.underfloor_ac as jjj_uf
import pytest

# 床下空調利用時の式(40)のテスト
class Test_熱源機の風量を計算するための熱源機の出力:

    def test_既存関数の計算(self):
        """
        熱源機の風量を計算するための熱源機の出力適正度合い_風量_40
        """
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)

        environment = jjj_ipt.EnvironmentEntity(input)
        climate = jjj_ipt.ClimateEntity(input.region)

        V_vent_l_d_t \
            = dc.get_V_vent_l_d_t(
                dc.get_V_vent_l_NR_d_t(),
                dc.get_V_vent_l_OR_d_t(),
                dc.get_V_vent_l_MR_d_t())

        # Act
        i = 0  # 01/01 01:00
        Q_hat_hs = jjj_uf.calc_Q_hat_hs(
            Q = environment.get_Q(),
            A_A = input.A_A,
            V_vent_l = V_vent_l_d_t[i],
            V_vent_g_i = environment.get_V_vent_g_i(),
            mu_H = environment.get_mu_H(),
            mu_C = environment.get_mu_C(),
            J = climate.get_J_d_t()[i],
            q_gen = environment.get_q_gen_d_t()[i],
            n_p = environment.get_n_p_d_t()[i],
            q_p_H = dc.get_q_p_H(),
            q_p_CS = dc.get_q_p_CS(),
            q_p_CL = dc.get_q_p_CL(),
            X_ex = climate.get_X_ex_d_t()[i],
            w_gen = environment.get_w_gen_d_t()[i],
            Theta_ex = climate.get_Theta_ex_d_t()[i],
            L_wtr = dc.get_L_wtr(),
            HCM = climate.get_HCM_d_t()[i],
        )

        # Assert
        assert Q_hat_hs is not None
        assert Q_hat_hs == pytest.approx(18.53, rel=1e-2)

    def test_床下温度の計算(self):
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)

        environment = jjj_ipt.EnvironmentEntity(input)
        climate = jjj_ipt.ClimateEntity(input.region)

        Theta_ex_d_t = climate.get_Theta_ex_d_t()
        Theta_in_d_t = uf.get_Theta_in_d_t('H')

        spec_MR, spec_OR = H.get_virtual_heating_devices(input.region, None, None)
        mode_MR, mode_OR = H.calc_heating_mode(input.region, H_MR=spec_MR, H_OR=spec_OR)

        L_H_d_t_i, _, _ = H.calc_heating_load(
            region = input.region,
            sol_region = input.sol_region,
            A_A = input.A_A,
            A_MR = input.A_MR,
            A_OR = input.A_OR,
            Q = environment.get_Q(),
            mu_H = environment.get_mu_H(),
            mu_C = environment.get_mu_C(),
            NV_MR = 0,  # 自然風利用しない
            NV_OR = 0,  # 自然風利用しない
            TS = input.TS,
            HEX = None,  # 熱交換換気なし
            r_A_ufvnt = None,  # 床下換気ナシ
            underfloor_insulation = True,  # 床下断熱アリ
            mode_H = '住戸全体を連続的に暖房する方式',
            mode_C = '住戸全体を連続的に冷房する方式',
            spec_MR = spec_MR,
            spec_OR = spec_OR,
            mode_MR = mode_MR,
            mode_OR = mode_OR,
            SHC = get_solarheat()
        )
        assert np.shape(L_H_d_t_i) == (12, 8760)

        r_A_uf_i = np.array(algo.get_table_e_6()).reshape(-1, 1)
        assert np.shape(r_A_uf_i) == (12, 1)

        # A_HCZ_i = environment.get_A_HCZ_i()
        # assert np.shape(A_HCZ_i) == (12, 1)
        # f1st_A_HCZ_i = r_A_uf_i * A_HCZ_i

        # Arrange - 当該住戸の空気を供給する床下空間に接する床の面積の合計 [m2]
        r_A_ufac = 1.0  # 床下空調利用時の有効率
        A_s_ufvnt_i \
            = np.array(
                [algo.calc_A_s_ufvnt_i(i, r_A_ufac, input.A_A, input.A_MR, input.A_OR) for i in range(1, 13)]
            ).reshape(-1, 1)
        assert np.shape(A_s_ufvnt_i) == (12, 1)
        A_s_ufvnt = np.sum(A_s_ufvnt_i)
        f1st_ratio = A_s_ufvnt / input.A_A

        L_H_d_t = np.sum(L_H_d_t_i, axis=0)
        f1st_L_H_d_t = f1st_ratio * L_H_d_t

        t = 0  # 01/01 01:00
        assert np.sum(f1st_L_H_d_t[t]) == pytest.approx(10.09, rel=1e-2)

        # Act
        V_dash_supply_1 = 339.1  # [m3/h]
        V_dash_supply_2 = 188.4  # [m3/h]
        V_dash_supply_flr1st = V_dash_supply_1 + V_dash_supply_2
        assert V_dash_supply_flr1st == pytest.approx(527.5, rel=1e-2)

        Theta_uf = jjj_uf.calc_Theta_uf(f1st_L_H_d_t[t], A_s_ufvnt, Theta_in_d_t[t], Theta_ex_d_t[t], V_dash_supply_flr1st)

        # Assert
        assert Theta_uf == pytest.approx(23.20, rel=1e-2)


    def test_床下空調用の床面積(self):
        """
        床下空調用の床面積 & 面積全体における割合
        """
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)

        # Act
        A_i = ld.get_table_10()
        r_A_uf_i = algo.get_table_e_6()
        A_uf_i = [r * a for r, a in zip(r_A_uf_i, A_i)]
        A_A_uf = sum(A_uf_i)

        # Assert
        assert A_A_uf == pytest.approx(65.4, rel=1e-2)
        assert A_A_uf / input.A_A == pytest.approx(0.54, rel=1e-2)

    def test_床下から居室への熱移動(self):
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)

        climate = jjj_ipt.ClimateEntity(input.region)
        Theta_in_d_t = uf.get_Theta_in_d_t('H')
        Theta_ex_d_t = climate.get_Theta_ex_d_t()

        # Arrange - 当該住戸の空気を供給する床下空間に接する床の面積の合計 [m2]
        r_A_ufac = 1.0  # 床下空調利用時の有効率
        A_s_ufvnt_i \
            = np.array(
                [algo.calc_A_s_ufvnt_i(i, r_A_ufac, input.A_A, input.A_MR, input.A_OR) for i in range(1, 13)]
            ).reshape(-1, 1)
        assert np.shape(A_s_ufvnt_i) == (12, 1)

        # Arrange - 暖冷房負荷計算時に想定した床の熱貫流率 [W/m2*K]
        environment = jjj_ipt.EnvironmentEntity(input)
        # CHEKC: どちらを使うか確認中
        U_s_vert = climate.get_U_s_vert(environment.get_Q())
        U_s = algo.get_U_s()

        # Act
        # NOTE: ここでは意図した空調ではなく漏れなので 通常の0.7となる
        H_floor = 0.7  # 床の温度差係数(-)
        t = 0
        assert Theta_in_d_t[t] > Theta_ex_d_t[t], "暖房期の前提"

        L_uf2room_d_i = \
            U_s * A_s_ufvnt_i \
            * (Theta_in_d_t[t] - Theta_ex_d_t[t]) * H_floor \
            * 3.6 / 1_000  # [W]->[MJ/h]

        # Assert
        assert np.shape(L_uf2room_d_i) == (12, 1)
        assert np.sum(L_uf2room_d_i) == pytest.approx(6.37, rel=1e-2)

    def test_床下から外気への熱損失(self):
        """
        床下から外気への熱損失
        """
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)

        environment = jjj_ipt.EnvironmentEntity(input)
        climate = jjj_ipt.ClimateEntity(input.region)
        psi = climate.get_psi(environment.get_Q())

        # Arrange - 基礎外周長さ [m]
        r_A_ufac = 1.0  # 床下空調利用時の有効率
        A_s_ufvnt_A = algo.get_A_s_ufvnt_A(r_A_ufac, input.A_A, input.A_MR, input.A_OR)
        L_uf = algo.get_L_uf(A_s_ufvnt_A)

        # Arrange - 外気温度 [℃]
        Theta_ex_d_t = climate.get_Theta_ex_d_t()

        # Act
        t = 0
        Theta_uf = 23.2  # 床下温度 [℃]
        L_uf2outdoor \
            = psi * L_uf * (Theta_uf - Theta_ex_d_t[0]) \
                * 3.6 / 1_000  # [W]->[MJ/h]

        # Assert
        assert L_uf2outdoor == pytest.approx(2.07, rel=1e-2)

    def test_床下から地盤への熱損失(self):

        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)
        R_g = input.R_g
        r_A_ufac = 1.0  # 床下空調利用時の床下面積の有効率
        A_s_ufvnt_A = algo.get_A_s_ufvnt_A(r_A_ufac, input.A_A, input.A_MR, input.A_OR)

        # 吸熱応答係数の初項
        Phi_A_0 = 0.025504994

        # Arrange - 地盤の不易層温度 [℃]
        climate = jjj_ipt.ClimateEntity(input.region)
        Theta_ex_d_t = climate.get_Theta_ex_d_t()
        Theta_g_avg = algo.get_Theta_g_avg(Theta_ex_d_t)

        # Act
        Theta_uf = 23.2
        # θ'_g_surf_A_m_d_t: 日付dの時刻tにおける 指数項mの 吸熱応答の項別成分 [℃]
        # TODO: これの算出も要テスト
        sum_Theta_dash_g_surf_A_m_d_t = 4.138

        L_uf2gnd_d_t \
            = (A_s_ufvnt_A / R_g) / (1 + Phi_A_0 / R_g) \
                * (Theta_uf - sum_Theta_dash_g_surf_A_m_d_t - Theta_g_avg) \
                * 3.6 / 1_000  # [W]->[MJ/h]

        # Assert
        assert L_uf2gnd_d_t == pytest.approx(4.51, rel=1e-2)
