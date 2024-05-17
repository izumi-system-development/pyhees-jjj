class TestInputPickups:
    """ 計算結果の確認をする前に入力値が想定したものかチェックするため
    """
    def __init__(self, q_rtd_C, q_rtd_H, q_max_C, q_max_H, e_rtd_C, e_rtd_H):
        self._q_rtd_C, self._q_rtd_H = q_rtd_C, q_rtd_H
        self._q_max_C, self._q_max_H = q_max_C, q_max_H
        self._e_rtd_C, self._e_rtd_H = e_rtd_C, e_rtd_H

    @property
    def q_rtd_C(self):
        """ Q[W]: 定格冷房能力(rated cooling capacity)
        """
        return self._q_rtd_C
    @property
    def q_rtd_H(self):
        """ Q[W]: 定格暖房能力(rated heating capacity)
        """
        return self._q_rtd_H
    @property
    def q_max_C(self):
        """ Q[W]: 最大冷房能力(max cooling capacity)
        """
        return self._q_max_C
    @property
    def q_max_H(self):
        """ Q[W]: 最大暖房能力(max heating capacity)
        """
        return self._q_max_H
    @property
    def e_rtd_C(self):
        """ 定格冷房エネルギー消費効率(efficiency of rated cooling)
        """
        return self._e_rtd_C
    @property
    def e_rtd_H(self):
        """ 定格暖房エネルギー消費効率(efficiency of rated heating)
        """
        return self._e_rtd_H


class ResultSummary:
    """ 計算結果をまとめて確認する
    """
    def __init__(self, E_C, E_H):
        self._E_C, self._E_H = E_C, E_H

    @property
    def E_C(self):
        """ 年当たりの冷房設備の設計一次エネルギー消費量[MJ/年] """
        return self._E_C
    @property
    def E_H(self):
        """ 年当たりの暖房設備の設計一次エネルギー消費量[MJ/年] """
        return self._E_H
