import os
import pytest
import numpy as np

import pyhees.section3_1_d as uf
import pyhees.section3_1_e as algo
import pyhees.section4_1 as HC
# JJJ
from jjjexperiment.input import get_solarheat
import jjjexperiment.inputs as jjj_ipt
import jjjexperiment.underfloor_ac as jjj_ufac
from jjjexperiment.app_config import *

class Test_床下空調時_式40:

    def test_既存関数の計算(self, Q_hat_hs_d_t):
        """
        (40) 熱源機の風量を計算するための熱源機の出力
        """
        # Arrange & Act
        t = 0  # 01/01 01:00
        # Assert
        assert Q_hat_hs_d_t is not None
        assert Q_hat_hs_d_t[t] == pytest.approx(18.53, rel=1e-2)


    def test_床下温度の計算(self):
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)

        environment = jjj_ipt.EnvironmentEntity(input)
        climate = jjj_ipt.ClimateEntity(input.region)

        Theta_ex_d_t = climate.get_Theta_ex_d_t()
        Theta_in_d_t = uf.get_Theta_in_d_t('H')

        spec_MR, spec_OR = HC.get_virtual_heating_devices(input.region, None, None)
        mode_MR, mode_OR = HC.calc_heating_mode(input.region, H_MR=spec_MR, H_OR=spec_OR)

        L_H_d_t_i, _, _ = HC.calc_heating_load(
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

        # Arrange - 当該住戸の空気を供給する床下空間に接する床の面積の合計 [m2]
        A_s_ufac_i, r_A_s_ufac = jjj_ufac.get_A_s_ufac_i(input.A_A, input.A_MR, input.A_OR)
        A_s_ufvnt = np.sum(A_s_ufac_i)

        L_H_d_t = np.sum(L_H_d_t_i, axis=0)
        L_H_d_t_flr1st = r_A_s_ufac * L_H_d_t

        t = 0  # 01/01 01:00
        assert np.sum(L_H_d_t_flr1st[t]) == pytest.approx(10.09, rel=1e-2)

        # Act
        V_dash_supply_1 = 339.1  # [m3/h]
        V_dash_supply_2 = 188.4  # [m3/h]
        V_dash_supply_flr1st = V_dash_supply_1 + V_dash_supply_2
        assert V_dash_supply_flr1st == pytest.approx(527.5, rel=1e-2)

        Theta_uf = jjj_ufac.calc_Theta_uf(L_H_d_t_flr1st[t], A_s_ufvnt, Theta_in_d_t[t], Theta_ex_d_t[t], V_dash_supply_flr1st)

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
        A_s_ufvnt_i, _ = jjj_ufac.get_A_s_ufac_i(input.A_A, input.A_MR, input.A_OR)
        A_s_ufvnt = np.sum(A_s_ufvnt_i)
        # Assert
        assert A_s_ufvnt == pytest.approx(65.44, rel=1e-2)
        assert A_s_ufvnt / input.A_A == pytest.approx(0.54, rel=1e-2)


    def test_床下から床上居室への熱移動(self):
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)

        app_config = injector.get(AppConfig)
        app_config.update(input.model_dump())

        climate = jjj_ipt.ClimateEntity(input.region)
        Theta_in_d_t = uf.get_Theta_in_d_t('H')
        Theta_ex_d_t = climate.get_Theta_ex_d_t()

        # Arrange - 当該住戸の空気を供給する床下空間に接する床の面積の合計 [m2]
        A_s_ufac_i, _ = jjj_ufac.get_A_s_ufac_i(input.A_A, input.A_MR, input.A_OR)
        A_s_ufac_A = np.sum(A_s_ufac_i)
        assert np.shape(A_s_ufac_i) == (12, 1)

        # Arrange - 暖冷房負荷計算時に想定した床の熱貫流率 [W/m2*K]
        environment = jjj_ipt.EnvironmentEntity(input)
        U_s_vert = climate.get_U_s_vert(environment.get_Q())
        # U_s = algo.get_U_s()

        # Act
        # NOTE: ここでは意図した空調ではなく漏れなので 通常の0.7となる
        H_floor = 0.7  # 床の温度差係数(-)
        t = 0
        assert Theta_in_d_t[t] > Theta_ex_d_t[t], "暖房期の前提"

        delta_L_uf2room \
            = jjj_ufac.calc_delta_L_room2uf_i(
                U_s_vert, A_s_ufac_i, Theta_in_d_t[t] - Theta_ex_d_t[t])

        # Assert
        assert np.shape(delta_L_uf2room) == (12, 1)
        assert np.sum(delta_L_uf2room) == pytest.approx(6.37, rel=1e-2)


    def test_床下から外気への熱損失(self):
        """
        床下から外気への熱損失
        """
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)

        environment = jjj_ipt.EnvironmentEntity(input)
        climate = jjj_ipt.ClimateEntity(input.region)
        phi = climate.get_phi(environment.get_Q())

        # Arrange - 基礎外周長さ [m]
        A_s_ufac_i, _ = jjj_ufac.get_A_s_ufac_i(input.A_A, input.A_MR, input.A_OR)
        L_uf = algo.get_L_uf(np.sum(A_s_ufac_i))

        # Arrange - 外気温度 [℃]
        Theta_ex_d_t = climate.get_Theta_ex_d_t()

        # Act
        t = 0
        Theta_uf = 23.2  # 床下温度 [℃]
        delta_L_uf2outdoor_d_t = np.vectorize(jjj_ufac.calc_delta_L_uf2outdoor)
        delta_L_uf2outdoor \
            = delta_L_uf2outdoor_d_t(phi, L_uf, Theta_uf - Theta_ex_d_t[t])

        # Assert
        assert delta_L_uf2outdoor == pytest.approx(2.07, rel=1e-2)


    def test_床下から地盤への熱損失(self):

        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)
        R_g = input.R_g
        A_s_ufac_i, r_A_s_ufac = jjj_ufac.get_A_s_ufac_i(input.A_A, input.A_MR, input.A_OR)

        # 吸熱応答係数の初項
        Phi_A_0 = 0.025504994

        # Arrange - 地盤の不易層温度 [℃]
        climate = jjj_ipt.ClimateEntity(input.region)
        Theta_ex_d_t = climate.get_Theta_ex_d_t()
        Theta_g_avg = algo.get_Theta_g_avg(Theta_ex_d_t)

        # Act
        Theta_uf = 23.2
        # θ'_g_surf_A_m_d_t: 日付dの時刻tにおける 指数項mの 吸熱応答の項別成分 [℃]
        sum_Theta_dash_g_surf_A_m = 4.138  # 算出方不明

        delta_L_uf2gnd_d_t = np.vectorize(jjj_ufac.calc_delta_L_uf2gnd)
        delta_L_uf2gnd \
            = delta_L_uf2gnd_d_t(
                np.sum(A_s_ufac_i), R_g, Phi_A_0, Theta_uf,
                sum_Theta_dash_g_surf_A_m, Theta_g_avg)

        # Assert
        assert delta_L_uf2gnd == pytest.approx(4.51, rel=1e-2)
