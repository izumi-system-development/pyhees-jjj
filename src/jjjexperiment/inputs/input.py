from jjjexperiment.inputs.options import *

# TODO: 使用している一つのテストをDIベースにして消去する
def get_basic(input: dict):
    """ 基本情報の設定

    Returns:
    (住宅タイプ, 住宅建て方, 床面積, 面積の合計[m2], 主たる居室の面積[m2], その他の居室の面積[m2], 地域区分, 年間日射地域区分)

    """
    # 住宅タイプ
    type = '一般住宅'

    # 住宅建て方
    tatekata = '戸建住宅'

    # 床面積
    A_A = float(input['A_A'])
    A_MR = float(input['A_MR'])
    A_OR = float(input['A_OR'])

    # 地域区分
    region = int(input['region'])

    # 年間日射地域区分
    sol_region = None

    return type, tatekata, A_A, A_MR, A_OR, region, sol_region

# TODO: クライアントコードをDIベースに変更して削除する
def get_solarheat():
    """太陽熱利用の設定

    :return: 太陽熱利用
    """
    # 太陽熱利用
    SHC = None

    return SHC
