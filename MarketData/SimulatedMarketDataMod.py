from .MarketDataMod import MarketData
from Helpers import cols_to_int

class SimulatedMarketData(MarketData):
    def __init__(self,md,t,curve_att):
        #self.md = cols_to_int(md[md['Date']==t])
        #self.t = t
        #self.ca = curve_att
        super().__init__(md,t,curve_att)

    def simulate(self, params, sc):
        name = self.md['Name'].iloc[0]
        type = self.ca[self.ca['Name'] == name]['Type'].iloc[0]
        base_scenario = md_mini[md_mini['Date'] == base_dt]