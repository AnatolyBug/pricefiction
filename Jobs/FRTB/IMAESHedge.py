import pandas as pd
from datetime import datetime
from MarketData import *
from Portfolios import *

class IMAESHedge:
    def __init__(self, request):
        self.request = request

    def run(self):
        K = 1349.59
        M = datetime.strptime('20/12/2020', '%d/%m/%Y')

        scenarios = int(self.request['Scenarios'])
        t = datetime.strptime(self.request['ValuationDate'], '%d/%m/%Y')
        md = pd.read_csv(self.request['MarketData'])
        md['Date'] = pd.to_datetime(md['Date'], format='%d/%m/%Y')
        ca = pd.read_csv(self.request['CurveAttributes'])
        md_ex = HistoricalMarketData(md, t, ca)

        opt = EQEuropeanCallOption('GOOG',K,M,'USD','VIX')
        s = Stock('GOOG', n=-0.57312)
        a = opt.delta(t,scenario=pd.Series(t), md=md_ex)
        pt = Portfolio([opt,s])
        aa= pt.delta(t,scenario=pd.Series(t), md=md_ex)

        portfolios = []
        for i in range(0,scenarios):
            portfolios.append(Portfolio.from_csv(self.request['Portfolio'],name=i))

        base_pr = portfolios[0].mtm(t, scenario=pd.Series(t), md=md_ex)
        base_dlt = portfolios[0].delta(t, scenario=pd.Series(t), md=md_ex)
        base_rho = portfolios[0].rho(t, scenario=pd.Series(t), md=md_ex)

        base_prices = pd.Series(list(base_pr) * scenarios)
        all_res = pd.DataFrame([[t]], columns=['ScenarioDate'])
        all_res['Price'] = base_pr
        sim = md_ex.simulate({'GOOG':10,'USD':10})
        md_ex_sim = HistoricalMarketData(sim, t, ca)
        scen_dts = pd.Series(md_ex_sim.md['Date'].unique())

        np.random.seed(4567)
        rand = np.random.randint(len(scen_dts), size=scenarios)
        rand_df = pd.DataFrame(rand, columns=['Scenario'])
        rand_scen_df = pd.merge(rand_df, md_ex_sim.md, left_on=['Scenario'], right_index=True, how='left')
        port_pr = portfolios[0].mtm(t, scenario=rand_scen_df['Date'], md=md_ex_sim)
        port_dlt = portfolios[0].rho(t, scenario=rand_scen_df['Date'], md=md_ex_sim)
        port_rho = portfolios[0].delta(t, scenario=rand_scen_df['Date'], md=md_ex_sim)
        returns = port_pr - base_prices
        '''
        rand_dates = rand_scen_df['Date']
        port_pr_1 = []
        port_dlt_1 = []
        port_rho_1 = []
        for port, dt in zip(portfolios, rand_dates):
            mtm = port.mtm(t, scenario=pd.Series(dt), md=md_ex_sim)
            dlt = port.delta(t, scenario=pd.Series(dt), md=md_ex_sim)
            rho = port.rho(t, scenario=pd.Series(dt), md=md_ex_sim)
            port_pr_1.append(mtm)
            port_dlt_1.append(dlt)
            port_rho_1.append(rho)
        '''
        a=1
        pass
