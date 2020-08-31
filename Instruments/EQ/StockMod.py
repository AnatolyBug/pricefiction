import pandas as pd

class Stock:
    def __init__(self, u, n=1, id=''):
        self.id = id
        self.U = u
        self.N = n
        self.interm_res = []

    @classmethod
    def from_csv(cls, args):
        id = args[0]
        U = args[1]
        N = float(args[2]) if args[2] else 1

        return cls(U, N, id)

    def price(self, t, scenario=None, md=None, pr_md=None, interm=False):
        sc = t if scenario is None else scenario
        pm = md.md_query(sc, S=self.U) if pr_md is None else pr_md
        if interm:
            pm['Scenario'] = sc.reset_index(drop=True)
            pm['ValuationDate'] = t
            self.interm_res.append(pm)
        return self.N*pm['S']

    def delta(self, t, scenario=None, md=None, pr_md=None):
        return pd.Series([self.N]*len(scenario))

    def vega(self, *args, **kwargs):
        return 0

    def rho(self, *args, **kwargs):
        return 0

    def __repr__(self):
        return 'Stock'