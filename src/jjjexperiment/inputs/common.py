from dataclasses import dataclass
from typing import Optional
# 床下
from pyhees.section3_2 import calc_r_env, get_Q_dash, get_mu_H, get_mu_C

@dataclass
class HouseInfo:
    """家に関する設定値"""

    type: str = '一般住宅'
    """住宅タイプ"""
    tatekata: str = '戸建住宅'
    """住宅建て方"""

    A_A: float = 120.08
    """床面積の合計 [m2]"""
    A_MR: float = 29.81
    """主たる居室の床面積 [m2]"""
    A_OR: float = 51.34
    """その他の居室の床面積 [m2]"""

    region: int = 6
    """地域区分"""
    sol_region: Optional[int] = None
    """年間日射地域区分"""

    @classmethod
    def from_dict(cls, data: dict) -> 'HouseInfo':
        kwargs = {}
        if 'A_A' in data:
            kwargs['A_A'] = float(data['A_A'])
        if 'A_MR' in data:
            kwargs['A_MR'] = float(data['A_MR'])
        if 'A_OR' in data:
            kwargs['A_OR'] = float(data['A_OR'])
        if 'region' in data:
            kwargs['region'] = int(data['region'])
        return cls(**kwargs)

@dataclass
class OuterSkin:
    """外皮に関する設定値"""

    # TODO: ドキュメント
    method: str = '当該住宅の外皮面積の合計を用いて評価する'
    A_env: float = 307.51
    A_A: float = 120.08  # ダブり
    U_A: float = 0.87
    eta_A_H: float = 2.8
    eta_A_C: float = 4.3

    NV_MR: float = 0
    """主たる居室における通風の利用における相当換気回数"""
    NV_OR: float = 0
    """その他の居室における通風の利用における相当換気回数"""
    TS: bool = False
    """蓄熱"""

    # NOTE: 現時点で入力反映なし 必要ならデータクラス化する
    SHC: Optional[dict] = None
    """太陽熱集熱式"""

    # NOTE: 現時点で入力反映なし 固定値
    YUCACO_r_A_ufvnt: float = (8.28+16.56+21.53) / (9.52+1.24+3.31+3.31+1.66+8.28+16.56+21.53)
    """空調空気を床下を通して給気する場合(YUCACO)の「床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)」"""

    r_A_ufvnt: Optional[float] = None
    """当該住戸において、床下空間全体の面積に対する 換気を供給する床下空間の面積の比 [-]"""
    # ▼ 床下空調利用時
    r_A_ufac: Optional[float] = None
    """当該住戸において、床下空間全体の面積に対する 空調を供給する床下空間の面積の比 [-]"""
    # NOTE: 新・旧 床下空調インプットによって決まる

    underfloor_air_conditioning_air_supply: bool = False
    """空調空気を床下を通して給気する(床下空調)"""
    underfloor_insulation: bool = False
    """床下空間の断熱"""
    hs_CAV: bool = False
    """全体風量を固定する"""

    r_env: Optional[float] = None
    """床面積の合計に対する外皮の部位の面積の合計の比 [-]"""
    Q: Optional[float] = None
    """熱損失係数"""
    mu_H: Optional[float] = None
    """暖房期の日射取得係数"""
    mu_C: Optional[float] = None
    """冷房期の日射取得係数"""

    @classmethod
    def from_dict(cls, data: dict) -> 'OuterSkin':
        kwargs = {}
        if 'A_env' in data:
            kwargs['A_env'] = float(data['A_env'])
        if 'A_A' in data:
            kwargs['A_A'] = float(data['A_A'])
        if 'U_A' in data:
            kwargs['U_A'] = float(data['U_A'])
        if 'eta_A_H' in data:
            kwargs['eta_A_H'] = float(data['eta_A_H'])
        if 'eta_A_C' in data:
            kwargs['eta_A_C'] = float(data['eta_A_C'])

        kwargs['r_env'] = calc_r_env(
                        method = '当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法',
                        A_env = kwargs.get('A_env', cls.A_env),
                        A_A = kwargs.get('A_A', cls.A_A))
        from pyhees.section3_1 import get_Q
        kwargs['Q'] = get_Q(get_Q_dash(kwargs.get('U_A', cls.U_A), kwargs.get('r_env', None)))
        kwargs['mu_H'] = get_mu_H(kwargs.get('eta_A_H', cls.eta_A_H), kwargs.get('r_env', None))
        kwargs['mu_C'] = get_mu_C(kwargs.get('eta_A_C', cls.eta_A_C), kwargs.get('r_env', None))

        # 床下換気
        if 'underfloor_ventilation' in data:
            if int(data['underfloor_ventilation']) == 2:
                # NOTE: パーセントで入力されているため
                kwargs['r_A_ufvnt'] = float(data['r_A_ufvnt']) / 100

        # 床下断熱
        if 'underfloor_insulation' in data:
            kwargs['underfloor_insulation'] = int(data['underfloor_insulation']) == 2

        # 床下空調
        if 'underfloor_air_conditioning_air_supply' in data:
            # 床下空調がオンです 強制的に、床下換気ナシ・床下断熱状態となります
            if int(data['underfloor_air_conditioning_air_supply']) == 2:
                kwargs['underfloor_air_conditioning_air_supply'] = True
                kwargs['underfloor_insulation'] = True
                kwargs['r_A_ufvnt'] = 0.0  # 床下換気なし

        if 'hs_CAV' in data:
            kwargs['hs_CAV'] = int(data['hs_CAV']) == 2

        return cls(**kwargs)

@dataclass
class HEX:
    """熱交換型換気の設定"""

    hex: bool = False
    """熱交換型換気の有無"""
    etr_t: float = 0.0
    """温度交換効率"""
    e_bal: float = 0.0
    """給気と排気の比率による温度交換効率の補正係数"""
    e_leak: float = 0.0
    """排気過多時における住宅外皮経由の漏気による温度交換効率の補正係数"""

    @classmethod
    def from_dict(cls, data: dict) -> 'HEX':
        kwargs = {}
        if 'HEX' in data and int(data['HEX']['install']) == 2:
            kwargs['hex'] = True
            kwargs['etr_t'] = float(data['HEX']['etr_t'])
            kwargs['e_bal'] = 0.9
            kwargs['e_leak'] = 1.0
        return cls(**kwargs)

    def to_dict(self) -> dict:
        if not self.hex:
            return None
        return {
            'hex': self.hex,
            'etr_t': self.etr_t,
            'e_bal': self.e_bal,
            'e_leak': self.e_leak
        }
