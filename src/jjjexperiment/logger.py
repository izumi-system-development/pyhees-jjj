import logging
from pathlib import Path
from inspect import stack
import numpy as np
import datetime
import functools

from os import path

LOG_LEVEL = logging.DEBUG  # NOTE: 調査に合わせて変更する

# LOG_PATH = path.join(path.dirname(path.dirname(__file__)), '/logs/test.log')
LOG_PATH = Path(path.join(path.dirname(__file__), '../logs/test.log')).resolve()
# NOTE: テスト実行時のルートからのパス
# HACK: 現在は単一のファイルを使いまわします

FORMAT = logging.Formatter('%(message)s')

def get_logger(name) -> logging.Logger:
    """ モジュール毎に使用する共通設定されたLoggerを取得する
    """
    file_hdler = logging.FileHandler(LOG_PATH)
    file_hdler.setFormatter(FORMAT)
    # NOTE: FileHandler.setLevel() 変更しても効果なし

    logger = logging.getLogger(name)
    logger.addHandler(file_hdler)
    logger.setLevel(LOG_LEVEL)
    return logger


class LimitedLoggerAdapter(logging.LoggerAdapter):
    """ Testコード経由のみでログを出力する
    """
    _isTest = False
    _logger: logging.Logger = None

    @classmethod
    def init_logger(cls):
        """ ログ出力ファイルの存在チェックと実行テスト名のメモ
            各テストで一度だけ呼ばれるようにして下さい
        """
        cls._isTest = True
        caller = stack()[1].function  # NOTE: 呼び出し元関数名の取得

        LOG_PATH.touch(exist_ok=True)
        with LOG_PATH.open(mode='w') as f:
            # NOTE: 記述をリセットしています
            f.write(caller + ' EXECUTED!\n')

        cls._logger = get_logger(caller)

    """ logger のフィルタリング """

    # def critical(cls, message):
    # def error(cls, message):
    # def warning(cls, message):
    # def info(cls, message):

    @classmethod
    def info(cls, message):
        if cls._isTest: cls._logger.info(message)
    @classmethod
    def debug(cls, message):
        if cls._isTest: cls._logger.debug(message)

    @classmethod
    def NDdebug(cls, label: str, arr: np.ndarray):
        if cls._isTest: cls._write_arr_info(label, arr)

    @classmethod
    def NDtoCSV(cls, label: str, arr: np.ndarray):
        if cls._isTest:
            now = datetime.datetime.now()
            # 混ぜると見にくいので別ファイルとする
            np.savetxt(label + now.strftime('%H%M%S') + '.csv', arr, delimiter=',')

    @classmethod
    def _write_arr_info(cls, label: str, arr: np.ndarray):
        if cls._isTest:
            cls._logger.debug(f"{label}[MAX]  : {max(arr)}")
            cls._logger.debug(f"{label}[ZEROS]: {arr.size - np.count_nonzero(arr)}")
            cls._logger.debug(f"{label}[AVG.] : {np.average(arr[np.nonzero(arr)])}")



# ロギング用デコレータ

def log_res(res_labels: list = []):
    """ デコレータでロガーを有効化します(返却値と同じ長さのラベルを渡して下さい """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)

            # Break
            if not LimitedLoggerAdapter._isTest: return res

            # 複数返却値
            if type(res) is tuple:
                if len(res) == len(res_labels):
                    for i, label in enumerate(res_labels):
                        if res[i] is np.ndarray:
                            if res[i].ndim > 1:
                                # FIXME: 二次元を前提でインデックス0固定にしています
                                LimitedLoggerAdapter.NDdebug(f"{func.__name__}.{label}", res[i][0])
                            else:
                                LimitedLoggerAdapter.NDdebug(f"{func.__name__}.{label}", res[i])
                        else:
                            # その他の型
                            LimitedLoggerAdapter.debug(f"{func.__name__}.{label}: {res[i]}")
                else:
                    LimitedLoggerAdapter.debug(f"[ERROR]{func.__name__} should be checked for log label.")

            # 単体返却値
            elif type(res) is np.ndarray:
                if res.ndim > 1:
                    # FIXME: 二次元を前提でインデックス0固定にしています
                    LimitedLoggerAdapter.NDdebug(func.__name__, res[0])
                else:
                    LimitedLoggerAdapter.NDdebug(func.__name__, res)
            else:
                # その他の型
                LimitedLoggerAdapter.debug(f"{func.__name__}: {res}")

            return res
        return wrapper
    return decorator
