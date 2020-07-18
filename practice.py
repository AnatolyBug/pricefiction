from scipy.stats import norm
import pandas as pd
import numpy as np
from math import sqrt, exp, log, pi
from Instruments import *
from MarketData import *


df = pd.DataFrame([[1,2,3],[4,np.nan,6],[7,7,7]],columns =[1,2,13])
#df1 = df.interpolate(method='cubic',axis=1)
#srs = pd.Series([88])
#df['D']=srs
s3 = pd.Series([10,10,11,12,13,9,80])

a = s3.pct_change(periods=2)
aa = s3.pct_change(periods=2)
pass