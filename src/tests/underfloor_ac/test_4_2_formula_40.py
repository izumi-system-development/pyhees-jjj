import os
import pyhees.section4_2 as dc

# JJJ
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
        input_data = jjj_ipt.load_input_yaml(yaml_fullpath)

        environment = jjj_ipt.EnvironmentEntity(input_data)
        climate = jjj_ipt.ClimateEntity(input_data.region)

        V_vent_l_d_t \
            = dc.get_V_vent_l_d_t(
                dc.get_V_vent_l_NR_d_t(),
                dc.get_V_vent_l_OR_d_t(),
                dc.get_V_vent_l_MR_d_t())

        # Act
        i = 0  # 01/01 01:00
        Q_hat_hs = jjj_uf.calc_Q_hat_hs(
            Q = environment.get_Q(),
            A_A = input_data.A_A,
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
