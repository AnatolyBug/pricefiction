import pandas as pd
from datetime import datetime
from MarketData import *
from Portfolios import *
from Instruments import *
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pylab

class IMAESAlt:
    def __init__(self, request):
        self.request = request

    def run(self):
        scenarios = int(self.request['Scenarios'])
        t = datetime.strptime(self.request['ValuationDate'], '%d/%m/%Y')
        md = pd.read_csv(self.request['MarketData'])
        md['Date'] = pd.to_datetime(md['Date'], format='%d/%m/%Y')
        ca = pd.read_csv(self.request['CurveAttributes'])
        md_ex = HistoricalMarketData(md, t, ca)

        base_portfolio = Portfolio.from_csv(self.request['Portfolio'])
        base_pr = base_portfolio.mtm(t, scenario=pd.Series(t), md=md_ex)
        base_prices = pd.Series(list(base_pr) * scenarios)
        all_res = pd.DataFrame([[t]], columns=['ScenarioDate'])
        all_res['Price'] = base_pr
        sim_join = md_ex.simulate({'GOOG':10,'USD':10, 'VIX':20})
        md_ex_sim = HistoricalMarketData(sim_join, t, ca)
        scen_dts = pd.Series(md_ex_sim.md['Date'].unique())
        #a = md_ex_sim.md[md_ex_sim.md['Name']=='VIX']
        #aa = md_ex_sim.md[md_ex_sim.md['Name'] == 'GOOG']

        np.random.seed(4567)
        rand = np.random.randint(len(scen_dts), size=scenarios)
        rand_df = pd.DataFrame(rand, columns=['Scenario'])
        rand_scen_df = pd.merge(rand_df, md_ex_sim.md, left_on=['Scenario'], right_index=True, how='left')
        port_pr = base_portfolio.mtm(t, scenario=rand_scen_df['Date'], md=md_ex_sim)

        returns = port_pr - base_prices
        returns.sort_values(inplace=True)
        var_975 = pd.Series(returns).quantile(0.025)

        i = 0
        below_var = 0
        while returns.iloc[i] < var_975:
            below_var += returns.iloc[i]
            i += 1
        es = below_var / i

        all_res_lh = pd.DataFrame()
        all_res_lh['RandomNumber'] = rand
        all_res_lh['ScenarioDate'] = rand_scen_df['Date']
        all_res_lh['Price'] = port_pr
        all_res_lh['Return'] = returns
        all_res_lh['VaR_975'] = pd.Series([var_975])
        all_res_lh['ES'] = pd.Series([es])
        all_res = all_res.append(all_res_lh, ignore_index=True)
        if self.request['ExportToCSV']:
            all_res.to_csv(r'Results\IMAAlt.csv', index=False)
        if self.request['ShowPlots']:
            ret1 = all_res['Return'].dropna()
            f = plt.figure(1)
            plt.hist(ret1, color='blue', edgecolor='black',
                     bins=20, density=True, figure=f)
            sm.qqplot(ret1, line='s')
            pylab.show()
            plt.show()
        pass