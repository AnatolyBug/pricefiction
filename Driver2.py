from Jobs import JobExecutioner as je

request = {
    'MarketData':r'Data\MarketData.csv',
    'CurveAttributes':r'Data\CurveAttributes.csv',
    'Portfolio':r'Data\PortfolioUH.csv',
    'ValuationDate':'20/12/2019',
    #'Scenarios':'200',
    'Scenarios':'1000',
    'Job':'IMAESHestonAge',
    #'Job':'IMAES',
    'ExportToCSV':True,
    'ShowPlots':True
}

je.Job().run(request)