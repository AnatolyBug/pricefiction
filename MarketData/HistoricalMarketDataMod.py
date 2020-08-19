import pandas as pd
import numpy as np
from Helpers.HelpersMod import lin_interp, cols_to_int, TTM
from .SimulationModels import *
from .MarketDataMod import MarketData

class HistoricalMarketData(MarketData):
    def __init__(self, md, t, curve_att=None):
        self.hist_md = cols_to_int(md)
        self.t = t
        self.ca = curve_att
        self.simulations = {}
        super().__init__(md,t,curve_att)



    def simulate(self, riskfactors, base_dt=None, intersection=True, drop=True, overlap=False):
        if base_dt is None:
            base_dt = self.t

        dfs_rfs = []
        dfs_other = []
        rfs_other=[]
        common_dates = self.hist_md['Date']

        dfs =[]
        _num_col = []

        #for name in riskfactors:
        for name in self.hist_md['Name'].unique():
            if drop:
                if name not in list(riskfactors.keys()):
                    #If name is not in riskf and drop==True then continue
                    continue

            md_mini = self.hist_md[self.hist_md['Name'] == name]
            if name in list(riskfactors.keys()):
                dfs_rfs.append(md_mini)
            else:
                #rfs_other.append(name)
                dfs_other.append(md_mini)
            if intersection:
                common_dates = common_dates[common_dates.isin(md_mini['Date'])]


        for md_mini in dfs_rfs:
            name = md_mini['Name'].iloc[0]
            type = self.ca[self.ca['Name']==name]['Type'].iloc[0]
            base_scenario = md_mini[md_mini['Date'] == base_dt]
            if not overlap:
                #Sim days based on period
                sim_dates = pd.date_range(start=common_dates.min(), end=common_dates.max(), freq=str(riskfactors[name]) + 'B')
                #overlapping will happen in pct_change
                md_simulated = md_mini[md_mini['Date'].isin(sim_dates)]
            else:
                md_simulated = md_mini.copy()

            md_simulated.set_index('Date', inplace=True)
            md_simulated.sort_index(inplace=True)
            md_simulated.dropna(axis=1,how='all', inplace=True)
            str_cols={}
            num_col = []
            for col in list(md_simulated):
                if isinstance(col,str):
                    str_cols[col]=md_simulated[col].iloc[0]
                    del md_simulated[col]
                else:
                    num_col.append(col)
                    _num_col.append(col)
            num_col.sort()
            md_simulated=md_simulated[num_col]
            if not overlap:
                md_simulated = md_simulated.pct_change()
            else:
                md_simulated = md_simulated.pct_change(periods=int(riskfactors[name]))
            md_simulated.replace(np.inf,np.nan,inplace=True)
            if type == 'YieldCurve':
                md_simulated.fillna(method='bfill', inplace=True, axis=1)
                md_simulated.fillna(method='ffill', inplace=True, axis=1)
            else:
                md_simulated.fillna(method ='bfill',inplace=True)
                md_simulated.fillna(method='ffill', inplace=True)
            for col in md_simulated:
                md_simulated[col] = (1 + md_simulated[col]) * base_scenario[col].iloc[0]

            for key, value in str_cols.items():
                md_simulated[key]=value
            dfs.append(md_simulated)

        sim = pd.concat(dfs)
        sim.reset_index(inplace=True)

        if intersection:
            if len(set(riskfactors.values())) > 1:
                common_dates2 = common_dates.copy()
                for name in sim['Name'].unique():
                    md_mini = sim[sim['Name'] == name]
                    common_dates2 = common_dates2[common_dates2.isin(md_mini['Date'])]

                sim = sim[sim['Date'].isin(common_dates2)]

        dfs_other_sim = []
        for df in dfs_other:
            base_scenario = df[df['Date'] == base_dt]
            df_non_sim=pd.DataFrame(sim['Date'],columns=['Date'])
            df_non_sim['Name']=base_scenario['Name'].iloc[0]
            for col in df.columns:
                if isinstance(col,int):
                    df_non_sim[col]=base_scenario[col].iloc[0]
            dfs_other_sim.append(df_non_sim)

        if dfs_other_sim:
            non_sim = pd.concat(dfs_other_sim)
            sim = sim.append(non_sim)


        sim.dropna(axis=0, how='all', inplace=True)

        return sim



    '''
    def get_r(self, scenario, dtm):
        scenario.dropna(axis=1,how='all', inplace=True)
        num_col = []
        for col in list(scenario):
            if isinstance(col, str):
                pass
            else:
                num_col.append(col)
        return lin_interp(dtm, scenario[num_col])
    '''



