from MarketData import *
from Instruments import *
from Portfolios import Portfolio
from datetime import datetime
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pylab
import scipy.stats as stats
# import matplotlib.mlab as mlab

class IMAES:
    def __init__(self, request):
        self.request = request

    def run(self):
        K = 1349.59
        scenarios = int(self.request['Scenarios'])
        BT = 10
        t = datetime.strptime(self.request['ValuationDate'], '%d/%m/%Y')
        M = datetime.strptime('20/12/2020', '%d/%m/%Y')
        md = pd.read_csv(self.request['MarketData'])
        md['Date'] = pd.to_datetime(md['Date'], format='%d/%m/%Y')
        ca = pd.read_csv(self.request['CurveAttributes'])
        lhs = np.sort(ca['LH'].unique())
        md_ex = HistoricalMarketData(md, t, ca)
        base_portfolio = Portfolio.from_csv(self.request['Portfolio'])
        #base_portfolio = Portfolio(EuropeanCallOption(K, M, 'GOOG', 'USD', 'VIX'), Stock('GOOG', notional=0.5721),name='Base')
        a = EQEuropeanCallOption('GOOG', K, M, 'USD', 'VIX')
        A = a.theta(t,md=md_ex)
        b = a.price(t,md=md_ex)
        base_pr = base_portfolio.mtm(t, scenario=pd.Series(t), md=md_ex)
        base_prices = pd.Series(list(base_pr) * scenarios)
        all_res = pd.DataFrame([[t]], columns=['ScenarioDate'])
        all_res['Price'] = base_pr

        for j in range(0, len(lhs)):
            lh = lhs[j]
            print(lh)
            rfs = ca[ca['LH'] >= lh]['Name']
            print(rfs)
            rfs_dict={}
            for rf in rfs:
                rfs_dict[rf]=BT

            sim = md_ex.simulate(rfs_dict, drop=False)
            md_10day_ex = HistoricalMarketData(sim, t, ca)
            scen_dts = pd.Series(md_10day_ex.md['Date'].unique())
            rand_scen = scen_dts.sample(n=scenarios, replace=True, random_state=4567)
            port_pr = base_portfolio.mtm(t, scenario=rand_scen, md=md_10day_ex,interm=True)
            inter = base_portfolio.products[0].interm_res[j]
            inter.to_csv('Interm_res_Option'+str(lh)+'_ES.csv',index=False)
            returns = port_pr - base_prices
            returns.sort_values(inplace=True)
            var_975 = pd.Series(returns).quantile(0.025)

            i = 0
            below_var = 0
            while returns.iloc[i] < var_975:
                below_var += returns.iloc[i]
                i += 1
            if i == 0:
                es = var_975
            else:
                es = below_var / i

            if j == 0:
                es_scaled = es
            else:
                coef = np.sqrt((lhs[j] - lhs[j - 1]) / BT)
                es_scaled = es * coef

            all_res_lh = pd.DataFrame()
            all_res_lh['ScenarioId'] = rand_scen.index
            all_res_lh['Price'] = port_pr
            all_res_lh['Return'] = returns
            all_res_lh['LH'] = lh
            all_res_lh['VaR_975'] = pd.Series([var_975])
            all_res_lh['ES'] = pd.Series([es])
            all_res_lh['ES_Scaled'] = pd.Series([es_scaled])
            all_res = all_res.append(all_res_lh, ignore_index=True)

        IMA_ES = np.sqrt((all_res['ES_Scaled'] ** 2).sum())
        all_res['IMA_ES'] = pd.Series([IMA_ES])
        if self.request['ExportToCSV']:
            all_res.to_csv(r'Results\IMAES.csv', index=False)
        if self.request['ShowPlots']:
            ret1 = all_res[all_res['LH']==10]['Return']
            ret2 = all_res[all_res['LH']==20]['Return']
            f = plt.figure(1)
            plt.hist(ret1, color='blue', edgecolor='black',
                     bins=20,density=True,figure=f)
            g=plt.figure(2)
            plt.hist(ret2, color='red', edgecolor='black',
                     bins=20, density=True,figure=g)

            sm.qqplot(ret1, line='s')
            sm.qqplot(ret2, line='s')
            pylab.show()
            plt.show()
