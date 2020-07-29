import pandas as pd
import numpy as np
from Helpers.HelpersMod import lin_interp, cols_to_int, TTM

class HistoricalMarketData:
    def __init__(self, md, t, curve_att=None):
        self.md = cols_to_int(md)
        self.t = t
        self.current_md = self.md[self.md['Date'] == t]
        self.ca = curve_att
        self.simulations = {}

    def simulate(self, riskfactors, base_dt=None, intersection=True, drop=True, overlap=False):
        if base_dt is None:
            base_dt = self.t

        dfs_rfs = []
        dfs_other = []
        common_dates = self.md['Date']

        dfs =[]
        _num_col = []

        #for name in riskfactors:
        for name in self.md['Name'].unique():
            if drop:
                if name not in list(riskfactors.keys()):
                    #If name is not in riskf and drop==True then continue
                    continue

            md_mini = self.md[self.md['Name'] == name]
            if name in list(riskfactors.keys()):
                dfs_rfs.append(md_mini)
            else:
                dfs_other.append(md_mini)
            if intersection:
                common_dates = common_dates[common_dates.isin(md_mini['Date'])]

        if not drop:
            for df in dfs_other:
                if intersection:
                    df = df[df['Date'].isin(common_dates)]


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
            a=set(riskfactors.values())
            if len(set(riskfactors.values())) > 1:
                common_dates2 = common_dates.copy()
                for name in sim['Name'].unique():
                    md_mini = sim[sim['Name'] == name]
                    common_dates2 = common_dates2[common_dates2.isin(md_mini['Date'])]

                sim = sim[sim['Date'].isin(common_dates2)]


        if dfs_other:
            non_sim = pd.concat(dfs_other)
            if intersection:
                non_sim = non_sim[non_sim['Date'].isin(sim['Date'])]
            sim = sim.append(non_sim)
        sim.dropna(axis=0, how='all', inplace=True)

        return sim

    def md_query(self, scen_dt, dtm=None,**kwargs):
        #print(scen_dt)
        scen_dt_df = pd.DataFrame(scen_dt,columns=['Date'])
        scenario_df = pd.merge(scen_dt_df,self.md,on=['Date'],how='left')
        d = pd.DataFrame()
        for key, value in kwargs.items():
            if value is not None:
                single_name = scenario_df[scenario_df['Name']==value]
                name = single_name['Name'].iloc[0]
                type = self.ca[self.ca['Name']==name]['Type'].iloc[0]
                single_name.reset_index(drop=True,inplace=True)
                if type=='YieldCurve':
                    d[key]=self.get_r(single_name,dtm)
                elif type == 'Stock' or type =='ImpVol':
                    d[key] = single_name[0]
            else:
                d[key] = 0

        return d

    def get_r(self, scenario, dtm):
        scenario.dropna(axis=1,how='all', inplace=True)
        num_col = []
        for col in list(scenario):
            if isinstance(col, str):
                pass
            else:
                num_col.append(col)
        return lin_interp(dtm, scenario[num_col])

    def DF(self,t,M,CCY,sc):
        ttm = TTM(t, M)
        df_r = self.md_query(sc,dtm=ttm.d,R=CCY)
        comp = self.ca[self.ca['Name']==CCY]['Compounding'].iloc[0]
        if comp == 'Continuous':
            return np.exp(-df_r['R']*ttm.y)

