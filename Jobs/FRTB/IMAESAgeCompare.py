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

class IMAESAgeCompare:
    def __init__(self, request):
        self.request = request

    def run(self):
        #K = 1349.59
        scenarios = int(self.request['Scenarios'])
        BT = 10
        t = datetime.strptime(self.request['ValuationDate'], '%d/%m/%Y')
        #M = datetime.strptime('20/12/2020', '%d/%m/%Y')
        md = pd.read_csv(self.request['MarketData'])
        md['Date'] = pd.to_datetime(md['Date'], format='%d/%m/%Y')
        ca = pd.read_csv(self.request['CurveAttributes'])
        lhs = ca['LH'].unique()
        md_ex = HistoricalMarketData(md, t, ca)
        base_portfolio = Portfolio.from_csv(self.request['Portfolio'])
        #base_portfolio = Portfolio(EuropeanCallOption(K, M, 'GOOG', 'USD', 'VIX'), Stock('GOOG', notional=0.5721),name='Base')
        base_pr = base_portfolio.mtm(t, scenario=pd.Series(t), md=md_ex,interm=True)
        inter = base_portfolio.products[0].interm_res[0]
        inter.to_csv('Interm_res_Base' + '.csv', index=False)
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

            sim = md_ex.simulate(rfs_dict)
            md_10day_ex = HistoricalMarketData(sim, t, ca)
            scen_dts = pd.Series(md_10day_ex.md['Date'].unique())
            np.random.seed(4567)
            rand = np.random.randint(len(scen_dts), size=scenarios)
            rand_df = pd.DataFrame(rand, columns=['Scenario'])
            rand_scen_df = pd.merge(rand_df, md_10day_ex.md, left_on=['Scenario'], right_index=True, how='left')
            port_pr = base_portfolio.mtm(t, scenario=rand_scen_df['Date'], md=md_10day_ex,interm=True)
            aged_port = base_portfolio.age_by_bd(lh)
            port_pr = aged_port.mtm(t, scenario=rand_scen_df['Date'], md=md_10day_ex, interm=True)
            inter = base_portfolio.products[0].interm_res[j]
            inter.to_csv('Interm_res_'+str(lh)+'.csv',index=False)
            returns = port_pr - base_prices
            returns.sort_values(inplace=True)
            var_975 = pd.Series(returns).quantile(0.025)

            i = 0
            below_var = 0
            while returns.iloc[i] < var_975:
                below_var += returns.iloc[i]
                i += 1
            es = below_var / i

            if j == 0:
                es_scaled = es
            else:
                coef = np.sqrt((lhs[j] - lhs[j - 1]) / BT)
                es_scaled = es * coef

            all_res_lh = pd.DataFrame()
            all_res_lh['RandomNumber'] = rand
            all_res_lh['ScenarioDate'] = rand_scen_df['Date']
            all_res_lh['Price'] = port_pr
            all_res_lh['Return'] = returns
            all_res_lh['LH'] = lh
            all_res_lh['VaR_975'] = pd.Series([var_975])
            all_res_lh['ES'] = pd.Series([es])
            all_res_lh['ES_Scaled'] = pd.Series([es_scaled])
            all_res = all_res.append(all_res_lh, ignore_index=True)

        IMA_ES = np.sqrt((all_res['ES_Scaled'] ** 2).sum())
        all_res['IMA_ES'] = pd.Series([IMA_ES])