import os
import pytest
import numpy as np

import pyhees.section3_1_d as uf
import pyhees.section3_2 as gihi
import pyhees.section4_1 as HC
import pyhees.section4_2 as dc
# JJJ
from jjjexperiment.inputs.common import HouseInfo, OuterSkin
from jjjexperiment.inputs.di_container import create_injector_from_json
from jjjexperiment.inputs.ac_setting import HeatingAcSetting, CoolingAcSetting
from jjjexperiment.underfloor_ac.inputs.common import UnderfloorAc

# 計算用エンティティ
from jjjexperiment.inputs.climate_entity import ClimateEntity
from jjjexperiment.inputs.environment_entity import EnvironmentEntity
from jjjexperiment.inputs.ac_quantity_entity import HeatQuantity, CoolQuantity

from jjjexperiment.underfloor_ac.section4_2 import get_A_s_ufac_i, calc_delta_L_room2uf_i

from test_utils.utils import *

# デバッグ用ロガー
from jjjexperiment.logger import LimitedLoggerAdapter as _logger, log_res

class Test_床下空調時_式8補正:

    def test_式8_補正計算例(self, Q_hat_hs_d_t):
        """
        (8) 熱損失を含む負荷バランス時の暖房負荷 補正
        """
        _logger.init_logger()
        # Arrange
        yaml_fullpath = os.path.join(os.path.dirname(__file__), 'test_input.yaml')
        injector = create_injector_from_json(load_input_yaml(yaml_fullpath))

        house = injector.get(HouseInfo)
        skin = injector.get(OuterSkin)
        new_ufac = injector.get(UnderfloorAc)
        heat_ac_setting = injector.get(HeatingAcSetting)
        cool_ac_setting = injector.get(CoolingAcSetting)

        _logger.info(f"UnderfloorAc config: {new_ufac}")

        climate = ClimateEntity(house.region, new_ufac)
        environment = EnvironmentEntity(house, skin)

        Theta_ex_d_t = climate.get_Theta_ex_d_t()
        Theta_in_d_t = uf.get_Theta_in_d_t('H')
        _logger.NDdebug("Theta_ex_d_t", Theta_ex_d_t)
        _logger.NDdebug("Theta_in_d_t", Theta_in_d_t)

        spec_MR, spec_OR = HC.get_virtual_heating_devices(house.region, None, None)
        mode_MR, mode_OR = HC.calc_heating_mode(house.region, H_MR=spec_MR, H_OR=spec_OR)

        _logger.debug(f"region: {house.region}")
        _logger.debug(f"A_A: {house.A_A}, A_MR: {house.A_MR}, A_OR: {house.A_OR}")
        _logger.debug(f"Q: {skin.Q}, mu_H: {skin.mu_H}, mu_C: {skin.mu_C}")

        L_H_d_t_i, _, _ = HC.calc_heating_load(
            region = house.region,
            sol_region = house.sol_region,
            A_A = house.A_A,
            A_MR = house.A_MR,
            A_OR = house.A_OR,
            Q = environment.get_Q(),
            mu_H = environment.get_mu_H(),
            mu_C = environment.get_mu_C(),
            NV_MR = 0,  # 自然風利用しない
            NV_OR = 0,  # 自然風利用しない
            TS = skin.TS,
            r_A_ufvnt = None,  # 床下換気ナシ
            HEX = None,  # 熱交換換気なし
            underfloor_insulation = True,  # 床下断熱アリ
            mode_H = '住戸全体を連続的に暖房する方式',
            mode_C = '住戸全体を連続的に冷房する方式',
            spec_MR = spec_MR,
            spec_OR = spec_OR,
            mode_MR = mode_MR,
            mode_OR = mode_OR,
            SHC = skin.SHC
        )
        t = 0  # 01/01 01:00
        _logger.NDdebug("L_H_d_t_i_1", L_H_d_t_i[0])
        _logger.NDdebug("L_H_d_t_i_2", L_H_d_t_i[1])
        _logger.NDdebug("L_H_d_t_i_3", L_H_d_t_i[2])
        _logger.NDdebug("L_H_d_t_i_4", L_H_d_t_i[3])
        _logger.NDdebug("L_H_d_t_i_5", L_H_d_t_i[4])
        assert np.shape(L_H_d_t_i) == (12, 8760)
        assert L_H_d_t_i[0][t] == pytest.approx(5.957, abs=1e-1)
        assert L_H_d_t_i[1][t] == pytest.approx(2.493, abs=1e-1)
        assert L_H_d_t_i[2][t] == pytest.approx(1.538, abs=1e-1)
        assert L_H_d_t_i[3][t] == pytest.approx(1.473, abs=1e-1)
        assert L_H_d_t_i[4][t] == pytest.approx(1.899, abs=1e-1)

        L_CS_d_t_i, _ = HC.calc_cooling_load(
            region = house.region,
            A_A = house.A_A,
            A_MR = house.A_MR,
            A_OR = house.A_OR,
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
            TS = skin.TS,
            HEX = None  # 熱交換換気なし
        )
        _logger.NDdebug('L_CS_d_t_i_1', L_CS_d_t_i[0])
        _logger.NDdebug('L_CS_d_t_i_2', L_CS_d_t_i[1])
        _logger.NDdebug('L_CS_d_t_i_3', L_CS_d_t_i[2])
        _logger.NDdebug('L_CS_d_t_i_4', L_CS_d_t_i[3])
        _logger.NDdebug('L_CS_d_t_i_5', L_CS_d_t_i[4])

        q_hs_rtd_H = HeatQuantity(heat_ac_setting, house.region, house.A_A).q_hs_rtd
        q_hs_rtd_C = CoolQuantity(cool_ac_setting, house.region, house.A_A).q_hs_rtd

        V_dash_hs_supply_d_t = dc.get_V_dash_hs_supply_d_t(
            V_hs_min = dc.get_V_hs_min(environment.get_V_vent_g_i()),
            V_hs_dsgn_H = heat_ac_setting.V_hs_dsgn,
            V_hs_dsgn_C = cool_ac_setting.V_hs_dsgn,
            Q_hs_rtd_H = dc.get_Q_hs_rtd_H(q_hs_rtd_H),
            Q_hs_rtd_C = dc.get_Q_hs_rtd_C(q_hs_rtd_C),
            Q_hat_hs_d_t = Q_hat_hs_d_t,  # fixture
            region = house.region)
        _logger.NDdebug('V_dash_hs_supply_d_t', V_dash_hs_supply_d_t)

        V_dash_supply_d_t_i = dc.get_V_dash_supply_d_t_i(
            r_supply_des_i = dc.get_r_supply_des_i(environment.get_A_HCZ_i()),
            V_dash_hs_supply_d_t = V_dash_hs_supply_d_t,
            V_vent_g_i = environment.get_V_vent_g_i()
        )
        _logger.NDdebug('V_dash_supply_d_t_1', V_dash_supply_d_t_i[0])
        _logger.NDdebug('V_dash_supply_d_t_2', V_dash_supply_d_t_i[1])
        _logger.NDdebug('V_dash_supply_d_t_3', V_dash_supply_d_t_i[2])
        _logger.NDdebug('V_dash_supply_d_t_4', V_dash_supply_d_t_i[3])
        _logger.NDdebug('V_dash_supply_d_t_5', V_dash_supply_d_t_i[4])

        # 床面積の合計に対する外皮の部位の面積の合計の比
        r_env = skin.r_env
        _logger.debug(f"r_env: {r_env}")

        A_prt_i = dc.get_A_prt_i(environment.get_A_HCZ_i(), r_env, house.A_MR, environment.get_A_NR(), house.A_OR)
        _logger.debug(f"A_prt_i: {A_prt_i}")
        _logger.debug(f"A_HCZ_i: {environment.get_A_HCZ_i()}")
        _logger.debug(f"A_NR: {environment.get_A_NR()}")

        Theta_star_HBR_d_t = dc.get_Theta_star_HBR_d_t(Theta_ex_d_t, climate.region)
        _logger.NDdebug('Theta_star_HBR_d_t', Theta_star_HBR_d_t)

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
            region = house.region
        )
        _logger.NDdebug('Theta_star_NR_d_t', Theta_star_NR_d_t)
        # NOTE: このθ*NRは既存式を利用しているが 式(52)にも改変を加えている
        # ここでは式(52)の改変は考慮しないため既存式を使用している

        Q_star_trs_prt_d_t_i = dc.get_Q_star_trs_prt_d_t_i(
            U_prt = dc.get_U_prt(),
            A_prt_i = A_prt_i,
            Theta_star_HBR_d_t = Theta_star_HBR_d_t,
            Theta_star_NR_d_t = Theta_star_NR_d_t
        )
        _logger.NDdebug('Q_star_trs_prt_d_t_1', Q_star_trs_prt_d_t_i[0])
        _logger.NDdebug('Q_star_trs_prt_d_t_2', Q_star_trs_prt_d_t_i[1])
        _logger.NDdebug('Q_star_trs_prt_d_t_3', Q_star_trs_prt_d_t_i[2])
        _logger.NDdebug('Q_star_trs_prt_d_t_4', Q_star_trs_prt_d_t_i[3])
        _logger.NDdebug('Q_star_trs_prt_d_t_5', Q_star_trs_prt_d_t_i[4])

        # Act
        # (8) 熱損失を含む負荷バランス時の暖房負荷
        L_star_H_d_t_i = dc.get_L_star_H_d_t_i(L_H_d_t_i, Q_star_trs_prt_d_t_i, house.region)
        _logger.NDdebug("L_star_H_d_t_i_1_before_correction", L_star_H_d_t_i[0])
        _logger.NDdebug("L_star_H_d_t_i_2_before_correction", L_star_H_d_t_i[1])
        _logger.NDdebug("L_star_H_d_t_i_3_before_correction", L_star_H_d_t_i[2])
        _logger.NDdebug("L_star_H_d_t_i_4_before_correction", L_star_H_d_t_i[3])
        _logger.NDdebug("L_star_H_d_t_i_5_before_correction", L_star_H_d_t_i[4])

        A_s_ufac_i, r_A_s_ufac = get_A_s_ufac_i(house.A_A, house.A_MR, house.A_OR)
        _logger.debug(f"A_s_ufac_i: {A_s_ufac_i}")
        _logger.debug(f"r_A_s_ufac: {r_A_s_ufac}")

        U_s_vert = climate.get_U_s_vert(environment.get_Q())
        _logger.debug(f"U_s_vert: {U_s_vert}")
        delta_L_uf2room_d_t_i = np.hstack([
            calc_delta_L_room2uf_i(
                U_s_vert, A_s_ufac_i,
                np.abs(Theta_star_HBR_d_t[tt] - Theta_ex_d_t[tt]))
            for tt in range(24*365)
        ])
        _logger.NDdebug("delta_L_uf2room_d_t_i_1", delta_L_uf2room_d_t_i[0])
        _logger.NDdebug("delta_L_uf2room_d_t_i_2", delta_L_uf2room_d_t_i[1])
        _logger.NDdebug("delta_L_uf2room_d_t_i_3", delta_L_uf2room_d_t_i[2])
        _logger.NDdebug("delta_L_uf2room_d_t_i_4", delta_L_uf2room_d_t_i[3])
        _logger.NDdebug("delta_L_uf2room_d_t_i_5", delta_L_uf2room_d_t_i[4])
        _logger.debug(f"Temperature difference at t=0: {np.abs(Theta_star_HBR_d_t[0] - Theta_ex_d_t[0])}")
        assert delta_L_uf2room_d_t_i.shape == (12, 8760)
        assert delta_L_uf2room_d_t_i[0][t] == pytest.approx(2.906, abs=1e-1)
        assert delta_L_uf2room_d_t_i[1][t] == pytest.approx(1.614, abs=1e-1)
        assert delta_L_uf2room_d_t_i[2][t] == pytest.approx(0, abs=1e-1)
        assert delta_L_uf2room_d_t_i[3][t] == pytest.approx(0, abs=1e-1)
        assert delta_L_uf2room_d_t_i[4][t] == pytest.approx(0, abs=1e-1)

        # (8) 補正
        L_star_H_d_t_i -= delta_L_uf2room_d_t_i[:5, :]  # 負荷控除
        _logger.NDdebug("L_star_H_d_t_i_1_after_correction", L_star_H_d_t_i[0])
        _logger.NDdebug("L_star_H_d_t_i_2_after_correction", L_star_H_d_t_i[1])
        _logger.NDdebug("L_star_H_d_t_i_3_after_correction", L_star_H_d_t_i[2])
        _logger.NDdebug("L_star_H_d_t_i_4_after_correction", L_star_H_d_t_i[3])
        _logger.NDdebug("L_star_H_d_t_i_5_after_correction", L_star_H_d_t_i[4])

        # Assert
        _logger.info(f"Final results at t={t}:")
        _logger.info(f"L_star_H_d_t_i[0][{t}] = {L_star_H_d_t_i[0][t]:.3f} (expected: 3.639)")
        _logger.info(f"L_star_H_d_t_i[1][{t}] = {L_star_H_d_t_i[1][t]:.3f} (expected: 1.308)")
        _logger.info(f"L_star_H_d_t_i[2][{t}] = {L_star_H_d_t_i[2][t]:.3f} (expected: 1.881)")
        _logger.info(f"L_star_H_d_t_i[3][{t}] = {L_star_H_d_t_i[3][t]:.3f} (expected: 1.752)")
        _logger.info(f"L_star_H_d_t_i[4][{t}] = {L_star_H_d_t_i[4][t]:.3f} (expected: 2.178)")
        assert L_star_H_d_t_i[0][t] == pytest.approx(3.639, abs=1e-1)
        assert L_star_H_d_t_i[1][t] == pytest.approx(1.308, abs=1e-1)
        assert L_star_H_d_t_i[2][t] == pytest.approx(1.881, abs=1e-1)
        assert L_star_H_d_t_i[3][t] == pytest.approx(1.752, abs=1e-1)
        assert L_star_H_d_t_i[4][t] == pytest.approx(2.178, abs=1e-1)
