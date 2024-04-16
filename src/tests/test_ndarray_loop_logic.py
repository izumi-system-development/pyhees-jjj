import pytest
import math

import numpy as np

class Test_配列操作の確認:

    def test_caplogic(self):
        """ 上限値反映テスト
        """
        arr_d_t_i = np.array([
            [3, 4, 5, 6, 7],
            [4, 3, 3, 6, 2],
            [3, 2, 5, 6, 1],
        ], dtype=float)
        arr_d_t = np.sum(arr_d_t_i, axis=0)  # 1d-shape(5, )
        mask_overflow = arr_d_t > 10  # 1d-shape(5, )
        ratios = np.divide(
            np.full(len(arr_d_t), 10, dtype=float),
            arr_d_t,
            where=mask_overflow, out=np.ones_like(arr_d_t, dtype=float))
        new_arr_d_t_i = np.multiply(
            arr_d_t_i,
            ratios[np.newaxis, :],
            where=mask_overflow, out=arr_d_t_i)

        # check
        check = np.sum(new_arr_d_t_i, axis=0)
        assert all(check <= 10)

    def test_LEVEL1(self):
        """ マスキング LV.1
        """
        arr = np.array([
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
        ])  # shape(3, 5)
        sum_arr = np.sum(arr[:, :], axis=0) # 1d-shape(5, )
        sum_arr = np.reshape(sum_arr, (1, len(sum_arr)))  # 2d-shape(1, 5)

        new_arr = np.divide(arr, sum_arr, where=sum_arr!=0)

        assert math.isclose(np.sum(new_arr[:, 0]), 1)
        assert math.isclose(np.sum(new_arr[:, 1]), 1)
        assert math.isclose(np.sum(new_arr[:, 2]), 1)
        assert math.isclose(np.sum(new_arr[:, 3]), 1)
        assert math.isclose(np.sum(new_arr[:, 4]), 1)

    def test_LEVEL2(self):
        """ マスキング LV.2
        """
        arr = np.array([
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
            [4, 5, 6, 7, 8],
            [5, 6, 7, 8, 9],
        ])  # shape(5, 5)
        sum_arr = np.sum(arr[:2, :], axis=0) # 1d-shape(5, )
        sum_arr = np.reshape(sum_arr, (1, len(sum_arr)))  # 2d-shape(1, 5)

        new_arr = np.divide(arr[:2, :], sum_arr, where=sum_arr!=0)

        assert math.isclose(np.sum(new_arr[:, 0]), 1)
        assert math.isclose(np.sum(new_arr[:, 1]), 1)
        assert math.isclose(np.sum(new_arr[:, 2]), 1)
        assert math.isclose(np.sum(new_arr[:, 3]), 1)
        assert math.isclose(np.sum(new_arr[:, 4]), 1)

    def test_LEVEL3(self):
        """ マスキング LV.3
        """
        arr = np.array([
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
            [4, 5, 6, 7, 8],
            [5, 6, 7, 8, 9],
        ])  # shape(5, 5)
        mask = np.array([True, False, True, True, True])
        sum_arr = np.sum(arr[:2, mask], axis=0) # 1d-shape(4, )
        sum_arr = np.reshape(sum_arr, (1, len(sum_arr)))  # 2d-shape(1, 4)

        new_arr = np.divide(arr[:2, mask], sum_arr, where=sum_arr!=0)

        assert math.isclose(np.sum(new_arr[:, 0]), 1)
        assert math.isclose(np.sum(new_arr[:, 1]), 1)
        assert math.isclose(np.sum(new_arr[:, 2]), 1)
        assert math.isclose(np.sum(new_arr[:, 3]), 1)

    def test_マスク合計(self):
        """ 二次元配列から虫食い状態で各行合計の取得
        """
        arr = np.array([
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5],
        ], dtype=float)
        mask = np.array([
            [True, False, True],
            [False, False, True],
            [True, True, True],
        ])
        masked_arr = np.where(mask, arr, 0)
        column_limited_sum = np.sum(masked_arr, axis=0)
        assert column_limited_sum[0] == 4
        assert column_limited_sum[1] == 4
        assert column_limited_sum[2] == 12

    def test_設計風量上限_案2_1段階(self):
        """ 増のセルのみへの影響でキャップするロジックのテスト
        """
        LIMIT_VAL = 10
        # V_dash_supply_d_t_i: 居室毎の風量仮に相当
        base_arr_d_t_i = np.array([
            [3, 4, 5, 3, 7],
            [3, 4, 5, 5, 7],
            [3, 4, 5, 2, 7],
        ], dtype=float)
        # V_supply_d_t_i: 判定前に相当
        arr_d_t_i = np.array([
            [3, 5, 6, 3, 8],
            [4, 4, 6, 8, 9],
            [5, 5, 6, 9, 2],
        ], dtype=float)
        arr_d_t = np.sum(arr_d_t_i, axis=0)

        # 設計風量を超えているか
        mask_overflow_d_t = arr_d_t > LIMIT_VAL  # 1d-shape
        mask_overflow_d_t_i = np.tile(mask_overflow_d_t, (3,1))
        print(np.shape(mask_overflow_d_t_i))

        # ベース配列を超えているか
        mask_beyond_d_t_i = arr_d_t_i > base_arr_d_t_i
        print(np.shape(mask_beyond_d_t_i))

        # マスクの合体
        mask_subtract_target_d_t_i = np.logical_and(mask_beyond_d_t_i, mask_overflow_d_t_i)

        # 各時間の削減量
        overflow_vals_d_t = arr_d_t - LIMIT_VAL  # 削減場所では限界値以上になっている

        # 元から制限を超えてしまってないか念のためチェックします
        mask_beyond_d_t = np.sum(mask_beyond_d_t_i, axis=0)
        # NOTE: 増加していないのに、制限を超えてしまっている時刻がないか
        errors = np.logical_and(mask_beyond_d_t == 0, overflow_vals_d_t > 0)
        assert not np.any(errors), "元から制限を超えている時刻があるようです."  # エラーなしを確認

        default_subtract_d_t_i = np.zeros_like(overflow_vals_d_t)
        # 各セルの削減量(各時間で共通)
        beyond_counts_d_t = np.sum(mask_subtract_target_d_t_i, axis=0)
        each_subtract_d_t = np.divide(
            overflow_vals_d_t,
            beyond_counts_d_t,
            where=beyond_counts_d_t>0, out=default_subtract_d_t_i)
        each_subtract_d_t_i = np.tile(each_subtract_d_t, (3, 1))

        result = np.where(
            mask_subtract_target_d_t_i,  # 引き算対象セル
            arr_d_t_i - each_subtract_d_t_i,
            arr_d_t_i)  # 引き算しない箇所

        check = np.sum(result, axis=0)
        assert all(check <= LIMIT_VAL)
