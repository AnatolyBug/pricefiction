import pandas as pd
from Helpers import TTM

class ZeroCouponBond:

    def __init__(self, M, ccy, notional = 100):
        self.N = notional
        self.M = M
        self.CCY = ccy

    def price(self, t, scenario=None, md=None, pr_md=None):
        sc = pd.Series(t) if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY) if pr_md is None else pr_md
        return self.N * exp(-pm['R'] * ttm.y)

    def vega(self, *args, **kwargs):
        return 0

    def rho(self, t, scenario=None, md=None, pr_md=None):
        sc = t if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY) if pr_md is None else pr_md
        return -self.price(t, pr_md=pm)*ttm.y

    def __repr__(self):
        return 'Zero Coupon Bond'