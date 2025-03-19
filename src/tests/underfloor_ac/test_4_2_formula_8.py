import os
import pytest
import numpy as np

import pyhees.section3_1 as ld
import pyhees.section3_1_d as uf
import pyhees.section3_1_e as algo
import pyhees.section3_2 as gihi
import pyhees.section4_1 as HC
import pyhees.section4_2 as dc
# JJJ
from jjjexperiment.input import get_solarheat
import jjjexperiment.inputs as jjj_ipt
import jjjexperiment.underfloor_ac as jjj_ufac

class Test_熱損失を含む負荷バランス時の暖冷房負荷:

    def test_既存関数の計算(self, Q_hat_hs_d_t):
        """
        熱損失を含む負荷バランス時の暖冷房負荷適正度合い_負荷_4_2
        """
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

        L_CS_d_t_i, _ = HC.calc_cooling_load(
            region = input.region,
            A_A = input.A_A,
            A_MR = input.A_MR,
            A_OR = input.A_OR,
            Q = environment.get_Q(),
            mu_H = environment.get_mu_H(),
            mu_C = environment.get_mu_C(),
            NV_MR = 0,  # 自然風利用しない
            NV_OR = 0,  # 自然風利用しない
            r_A_ufvnt = None,  # 床下換気ナシ
            underfloor_insulation = True,  # 床下断熱アリ
            mode_C = '住戸全体を連続的に冷房する方式',
            mode_H = '住戸全体を連続的に暖房する方式',
            mode_MR = mode_MR,
            mode_OR = mode_OR,
            TS = input.TS,
            HEX = None  # 熱交換換気なし
        )

        V_dash_hs_supply_d_t = dc.get_V_dash_hs_supply_d_t(
            V_hs_min = dc.get_V_hs_min(environment.get_V_vent_g_i()),
            V_hs_dsgn_H = input.H_A.V_hs_dsgn_H,
            V_hs_dsgn_C = input.C_A.V_hs_dsgn_C,
            Q_hs_rtd_H = dc.get_Q_hs_rtd_H(environment.get_q_hs_rtd_H()),
            Q_hs_rtd_C = dc.get_Q_hs_rtd_C(environment.get_q_hs_rtd_C()),
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

        Theta_star_HBR_d_t = dc.get_Theta_star_HBR_d_t(Theta_ex_d_t, climate.region)
        Theta_star_NR_d_t = dc.get_Theta_star_NR_d_t(
            Theta_star_HBR_d_t = Theta_star_HBR_d_t,
            Q = environment.get_Q(),
            A_NR = environment.get_A_NR(),
            V_vent_l_NR_d_t = environment.get_V_vent_l_NR_d_t(),
            V_dash_supply_d_t_i = V_dash_supply_d_t_i,
            U_prt = dc.get_U_prt(),
            A_prt_i = A_prt_i,
            L_H_d_t_i = L_H_d_t_i,
            L_CS_d_t_i = L_CS_d_t_i,
            region = input.region
        )

        Q_star_trs_prt_d_t_i = dc.get_Q_star_trs_prt_d_t_i(
            U_prt = dc.get_U_prt(),
            A_prt_i = A_prt_i,
            Theta_star_HBR_d_t = Theta_star_HBR_d_t,
            Theta_star_NR_d_t = Theta_star_NR_d_t
        )

        # Act
        i = 0  # 01/01 01:00
        L_star_H_d_t_i = dc.get_L_star_H_d_t_i(L_H_d_t_i, Q_star_trs_prt_d_t_i, input.region)
        assert L_star_H_d_t_i[0][i] == pytest.approx(6.545, rel=1e-2)

        A_s_ufac_i, r_A_s_ufac = jjj_ufac.get_A_s_ufac_i(input.A_A, input.A_MR, input.A_OR)

        U_s = dc.get_U_s()
        delta_L_uf2room_d_t_i = np.hstack([
            jjj_ufac.calc_delta_L_room2uf_i(U_s, A_s_ufac_i, Theta_star_HBR_d_t[tt] - Theta_ex_d_t[tt])
            for tt in range(24*365)
        ])
        assert delta_L_uf2room_d_t_i.shape == (12, 8760)
        L_star_H_d_t_i -= delta_L_uf2room_d_t_i[:5, :]  # 負荷控除

        # Assert
        assert L_star_H_d_t_i[0][i] == pytest.approx(3.60, rel=1e-2)
