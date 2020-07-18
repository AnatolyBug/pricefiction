from scipy.stats import norm
import numpy as np
import pandas as pd
from Helpers.HelpersMod import TTM
from datetime import datetime
from math import pi

class EuropeanEQOption:
    def __init__(self,u,k,m,ccy,vol,n=1,div=None,id=''):
        self.id = id
        self.N=n
        self.U = u
        self.K = k
        self.M = m
        self.CCY = ccy
        self.VOL= vol
        self.DIV = div



    @classmethod
    def from_csv(cls, args):
        id = args[0]
        U = args[1]
        N = float(args[2]) if args[2] else 1
        K = float(args[3])
        M = datetime.strptime(args[4], '%d/%m/%Y')
        CCY = args[5]
        VOL = args[6]
        DIV = args[7] if 7 < len(args) else None

        return cls(U, K, M, CCY, VOL, N, DIV, id)


    @staticmethod
    def phi(x):
        return np.exp((-x**2)/2)/np.sqrt(2*pi)

    def vega(self, t=None, scenario=None, md=None, pr_md=None):
        sc = t if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY, S=self.U, q=self.DIV, v=self.VOL) if pr_md is None else pr_md
        return self.N*pm['S']*exp(-pm['q']*ttm.y)*sqrt(ttm.y)*self.phi(self.d1(t, sc, pr_md=pm))

    def d1(self, t, scenario=None, md=None, pr_md=None):
        sc = pd.Series(t) if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY, S=self.U, q=self.DIV, v=self.VOL) if pr_md is None else pr_md
        return (np.log(pm['S']/self.K)+(pm['R']-pm['q']+(pm['v']**2)/2)*ttm.y) / pm['v'] / np.sqrt(ttm.y)

    def d2(self, t, scenario=None, md=None, pr_md=None):
        sc = pd.Series(t) if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY, S=self.U, q=self.DIV, v=self.VOL) if pr_md is None else pr_md
        return self.d1(t, sc, pr_md=pm) - pm['v'] * np.sqrt(ttm.y)

class EQEuropeanCallOption(EuropeanEQOption):
    def price(self, t, scenario=None, md=None, pr_md=None):
        sc = t if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY, S=self.U, q=self.DIV, v=self.VOL) if pr_md is None else pr_md
        return self.N*pm['S']*np.exp(-pm['q']*ttm.y)*norm.cdf(self.d1(t,pr_md=pm)) - self.N*self.K*np.exp(-pm['R']*ttm.y)*norm.cdf(self.d2(t,pr_md=pm))

    def delta(self, t, scenario=None, md=None, pr_md=None):
        sc = t if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY, S=self.U, q=self.DIV, v=self.VOL) if pr_md is None else pr_md
        return self.N*np.exp(-pm['q']*ttm.y)*norm.cdf(self.d1(t,pr_md=pm))

    def rho(self, t, scenario=None, md=None, pr_md=None):
        sc = t if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY, S=self.U, q=self.DIV, v=self.VOL) if pr_md is None else pr_md
        return self.N*self.K*ttm.y*np.exp(-pm['R']*ttm.y)*norm.cdf(self.d2(t,pr_md=pm))

    def __repr__(self):
        return 'European Call Option'

class EQEuropeanPutOption(EuropeanEQOption):

    def price(self, t, scenario=None, md=None, pr_md=None):
        sc = t if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY, S=self.U, q=self.DIV, v=self.VOL) if pr_md is None else pr_md
        return self.N*self.K*exp(-pm['R']*ttm.y)*norm.cdf(-self.d2(t,pr_md=pm)) - self.N*pm['S']*exp(-pm['q']*ttm.y)*norm.cdf(-self.d1(t,pr_md=pm))

    def delta(self, t, scenario=None, md=None, pr_md=None):
        sc = t if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY, S=self.U, q=self.DIV, v=self.VOL) if pr_md is None else pr_md
        return -self.N*exp(-pm['q']*ttm.y)*norm.cdf(-self.d1(t,pr_md=pm))

    def rho(self, t, scenario=None, md=None, pr_md=None):
        sc = t if scenario is None else scenario
        ttm = TTM(t, self.M)
        pm = md.md_query(sc, ttm.d, R=self.CCY, S=self.U, q=self.DIV, v=self.VOL) if pr_md is None else pr_md
        return self.N*self.K*ttm.y*exp(-pm['R']*ttm.y) * norm.cdf(-self.d2(t,pr_md=pm))

    def __repr__(self):
        return 'European Put Option'