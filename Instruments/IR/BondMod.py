import pandas as pd
import numpy as np
from datetime import datetime
from Helpers import TTM

class ZeroCouponBond:

    def __init__(self, M, ccy, notional = 100, id = ''):
        self.id = id
        self.N = notional
        self.M = M
        self.CCY = ccy

    @classmethod
    def from_csv(cls, args):
        id = args[0]
        N = float(args[1]) if args[1] else 100
        M = datetime.strptime(args[2], '%d/%m/%Y')
        CCY = args[3]


        return cls(M, CCY, notional=N, id=id)

    def price(self, t, scenario=None, md=None, pr_md=None):
        sc = pd.Series(t) if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY) if pr_md is None else pr_md
        return self.N * np.exp(-pm['R'] * ttm.y)

    def vega(self, t, scenario=None, md=None, pr_md=None):
        return 0

    def rho(self, t, scenario=None, md=None, pr_md=None):
        sc = pd.Series(t) if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY) if pr_md is None else pr_md
        return -self.price(t, pr_md=pm)*ttm.y

    def __repr__(self):
        return 'Zero Coupon Bond'