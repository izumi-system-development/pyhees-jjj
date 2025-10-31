import os
import pytest
import numpy as np

import pyhees.section3_2 as gihi
import pyhees.section4_1 as HC
import pyhees.section4_2 as dc
# JJJ
from jjjexperiment.common import *
from jjjexperiment.inputs.options import *
from jjjexperiment.inputs.di_container import *
from jjjexperiment.inputs.app_config import *
from jjjexperiment.inputs.input import get_solarheat
import jjjexperiment.inputs as jjj_ipt
import jjjexperiment.underfloor_ac as jjj_ufac

class Test_床下空調時_式52:

    @classmethod
    def setup_class(cls):
        """テストクラス共通設定"""
        app_config = injector.get(AppConfig)
        app_config.new_ufac_flg = 床下空調ロジック.変更する.value

    def test_式52_時点計算例(self, Q_hat_hs_d_t):
        """
        (52) 負荷バランス時の非居室の室温 [℃]
        """
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        input = jjj_ipt.load_input_yaml(yaml_fullpath)
        environment = jjj_ipt.EnvironmentEntity(input)
        climate = jjj_ipt.ClimateEntity(input.region)
        H_A = jjj_ipt.ArgHEntity(input)

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
            r_A_ufvnt = None,  # 床下換気ナシ
            HEX = None,  # 熱交換換気なし
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

        V_hs_dsgn_H, V_hs_dsgn_C = H_A.get_V_hs_dsgn_H()

        V_dash_hs_supply_d_t = dc.get_V_dash_hs_supply_d_t(
            V_hs_min = dc.get_V_hs_min(environment.get_V_vent_g_i()),
            V_hs_dsgn_H = V_hs_dsgn_H,
            V_hs_dsgn_C = V_hs_dsgn_C,
            Q_hs_rtd_H = dc.get_Q_hs_rtd_H(environment.get_q_hs_rtd_H()),
            Q_hs_rtd_C = None,  # 暖房時は初期化しない
            Q_hat_hs_d_t = Q_hat_hs_d_t,  # fixture
            region = input.region)

        V_dash_supply_d_t_i = dc.get_V_dash_supply_d_t_i(
            r_supply_des_i = dc.get_r_supply_des_i(environment.get_A_HCZ_i()),
            V_dash_hs_supply_d_t = V_dash_hs_supply_d_t,
            V_vent_g_i = environment.get_V_vent_g_i()
        )

        # 床面積の合計に対する外皮の部位の面積の合計の比
        r_env = gihi.calc_r_env(
            method='当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法',
            A_env=input.A_env,
            A_A=input.A_A
        )
        A_prt_i = dc.get_A_prt_i(environment.get_A_HCZ_i(), r_env, input.A_MR, environment.get_A_NR(), input.A_OR)
        assert A_prt_i.shape == (5,)
        A_prt_A = np.sum(A_prt_i)

        # Act
        t = 0  # 01/01 01:00
        L_H_NR_A = np.sum(L_H_d_t_i[5:, t])
        assert V_dash_supply_d_t_i.shape == (5, 8760)
        V_dash_supply_A = np.sum(V_dash_supply_d_t_i[0:5, t:t+1])

        Theta_star_NR = jjj_ufac.get_Theta_star_NR(
            Theta_star_HBR = 20.0,
            Q = environment.get_Q(),
            A_NR = environment.get_A_NR(),
            V_vent_l_NR = environment.get_V_vent_l_NR_d_t()[t],
            V_dash_supply_A = V_dash_supply_A,
            U_prt = dc.get_U_prt(),
            A_prt_A = A_prt_A,
            L_H_NR_A = L_H_NR_A,
            L_CS_NR_A = 0,
            Theta_NR = 20.0,
            Theta_uf = 23.2,
            HCM = climate.get_HCM_d_t()[t])

        # Assert
        assert L_H_NR_A == pytest.approx(5.17, abs=1e-2)
        assert Theta_star_NR == pytest.approx(19.39, abs=1e-2)
