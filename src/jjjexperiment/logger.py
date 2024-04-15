import logging
from pathlib import Path
from inspect import stack
import numpy as np
import datetime

from os import path

LOG_LEVEL = logging.DEBUG  # NOTE: 調査に合わせて変更する

# LOG_PATH = path.join(path.dirname(path.dirname(__file__)), '/logs/test.log')
LOG_PATH = Path('./logs/test.log')  # NOTE: テスト実行時のルートからのパス
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

    @classmethod
    def critical(cls, message):
        if cls._isTest: cls._logger.critical(message)
    @classmethod
    def error(cls, message):
        if cls._isTest: cls._logger.error(message)
    @classmethod
    def warning(cls, message):
        if cls._isTest: cls._logger.warning(message)
    @classmethod
    def info(cls, message):
        if cls._isTest: cls._logger.info(message)
    @classmethod
    def debug(cls, message):
        if cls._isTest: cls._logger.debug(message)

    @classmethod
    def NDdebug(cls, name: str, arr: np.ndarray):
        if cls._isTest:
            cls._logger.debug(f"{name}[MAX]  : {max(arr)}")
            cls._logger.debug(f"{name}[ZEROS]: {arr.size - np.count_nonzero(arr)}")
            cls._logger.debug(f"{name}[AVG.] : {np.average(arr[np.nonzero(arr)])}")

    @classmethod
    def NDtoCSV(cls, name: str, arr: np.ndarray):
        if cls._isTest:
            now = datetime.datetime.now()
            # 混ぜると見にくいので別ファイルとする
            np.savetxt(name + now.strftime('%H%M%S') + '.csv', arr, delimiter=',')
