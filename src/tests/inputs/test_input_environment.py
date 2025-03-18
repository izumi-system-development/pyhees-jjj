import numpy as np
import pytest

@pytest.mark.usefixtures('environment_entity')
class Test_Input_Environment:

    yaml_filename = "inputs/test_input.yaml"

    def test_get_mu_H(self, environment_entity):
        """
        get_mu_H をテスト
        """
        # Act
        mu_H = environment_entity.get_mu_H()
        # Assert
        assert mu_H is not None

    def test_get_mu_C(self, environment_entity):
        """
        get_mu_C をテスト
        """
        # Act
        mu_C = environment_entity.get_mu_C()
        # Assert
        assert mu_C is not None

    def test_get_V_vent_g_i(self, environment_entity):
        """
        get_V_vent_g_i をテスト
        """
        # Act
        V_vent_g_i = environment_entity.get_V_vent_g_i()
        # Assert
        assert V_vent_g_i is not None
        assert np.shape(V_vent_g_i) == (5,)

    def test_get_q_gen_d_t(self, environment_entity):
        """
        get_q_gen_d_t をテスト
        """
        # Act
        q_gen_d_t = environment_entity.get_q_gen_d_t()
        # Assert
        assert q_gen_d_t is not None
        assert np.shape(q_gen_d_t) == (8760,)

    def test_get_n_p_d_t(self, environment_entity):
        """
        get_n_p_d_t をテスト
        """
        # Act
        n_p_d_t = environment_entity.get_n_p_d_t()
        # Assert
        assert n_p_d_t is not None
        assert np.shape(n_p_d_t) == (8760,)

    def test_get_w_gen_d_t(self, environment_entity):
        """
        get_w_gen_d_t をテスト
        """
        # Act
        w_gen_d_t = environment_entity.get_w_gen_d_t()
        # Assert
        assert w_gen_d_t is not None
        assert np.shape(w_gen_d_t) == (8760,)

    def test_get_Q(self, environment_entity):
        """
        get_Q をテスト
        """
        # Act
        Q = environment_entity.get_Q()
        # Assert
        assert Q is not None
