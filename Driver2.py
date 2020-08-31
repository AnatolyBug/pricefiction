from Jobs import JobExecutioner as je

request = {
    'MarketData':r'Data\MarketData.csv',
    'CurveAttributes':r'Data\CurveAttributes.csv',
    'Portfolio':r'Data\PortfolioOpt.csv',
    'ValuationDate':'20/12/2019',
    'Scenarios':'200',
    'Job':'IMAESAltAge',
    'ExportToCSV':True,
    'ShowPlots':False
}

je.Job().run(request)