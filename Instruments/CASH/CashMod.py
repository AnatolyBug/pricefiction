from datetime import datetime
import pandas as pd

class Cash:
    def __init__(self, amount, maturity, disc_curve, id =''):
        self.A = amount
        self.M = maturity
        self.CCY = disc_curve

    @classmethod
    def from_csv(cls, args):
        id = args[0]
        A = args[1]
        M = datetime.strptime(args[2], '%d/%m/%Y')
        CCY = args[3]

        return cls(A, M, CCY, id)

    def price(self, t, scenario=None, md=None, pr_md=None):
        sc = pd.Series(t) if scenario is None else scenario
        df = md.DF(t, sc, self.M, self.CCY) if 'DF' not in pr_md else pr_md['DF']
        return self.A*df

