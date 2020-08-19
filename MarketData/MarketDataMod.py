from .SimulationModels import *
from Helpers import lin_interp, TTM, cols_to_int
import pandas as pd
import numpy as np

class MarketData:
    def __init__(self,md,t,curve_att):
        self.md = cols_to_int(md)
        self.current_md = self.md[self.md['Date']==t]
        self.t = t
        self.ca = curve_att

    def get_r(self, scenario, dtm):
        scenario.dropna(axis=1,how='all', inplace=True)
        num_col = []
        for col in list(scenario):
            if isinstance(col, str):
                pass
            else:
                num_col.append(col)

        return lin_interp(dtm, scenario[num_col])

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

    def DF(self,t,M,CCY,sc):
        ttm = TTM(t, M)
        df_r = self.md_query(sc,dtm=ttm.d,R=CCY)
        comp = self.ca[self.ca['Name']==CCY]['Compounding'].iloc[0]
        if comp == 'Continuous':
            return np.exp(-df_r['R']*ttm.y)

    def MCsimulation(self, params, drop=False):
        if params['Model']=='Heston':
            n_scen = int(params['Scenarios'])
            rfs = [params['Stock'],params['Vol']]
            non_rfs = self.current_md[~self.current_md['Name'].isin(rfs)]['Name'].unique()
            non_rfs_dfs = []
            for name in non_rfs:
                a = self.current_md[self.current_md['Name'] == name].copy()
                b = pd.concat([a] * n_scen, ignore_index=True)
                b['Date'] = range(0, n_scen)
                non_rfs_dfs.append(b)

            s0=self.current_md[self.current_md['Name']==params['Stock']][0].iloc[0]
            v0=self.current_md[self.current_md['Name']==params['Vol']][0].iloc[0]

            horizon=params['Horizon']
            seed = params['Seed'] if 'Seed' in params else None
            s_stop = params['S_stop'] if 'S_stop' in params else None
            v_stop = params['V_stop'] if 'V_stop' in params else None
            S_sim = []
            V_sim = []
            non_sim=[]
            scen_lst = []
            for scenario in range(0,n_scen):
                scen_lst.append(scenario)
                sim = Heston(mu=0.5,rho=0.1,kappa=2,theta=0.15,xi = 0.2).simulate(s0,v0,horizon,s_stop,v_stop,_seed=seed)
                S_sim.append(sim[0][horizon-1])
                V_sim.append(sim[1][horizon-1])
                if seed:
                    seed += 1
                '''
                POTENTIALLY TO BE USED LATER - SLOW WARNING
                for name in list(non_rfs_dict_df.keys()):
                    a = self.current_md[self.current_md['Name']==name]
                    a['Date'] = scenario
                    non_rfs_dict_df[name] = non_rfs_dict_df[name].append(a,ignore_index=True)
                '''



            S_df = pd.DataFrame(data={'Date':scen_lst,0:S_sim})
            S_df['Name'] = params['Stock']
            V_df = pd.DataFrame(data={'Date':scen_lst,0:V_sim})
            V_df['Name'] = params['Vol']
            df = S_df.append(V_df,ignore_index=True)
            for _df in non_rfs_dfs:
                df = df.append(_df,ignore_index=True)

            return MarketData(df,0,self.ca)
