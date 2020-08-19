import numpy as np
import pandas as pd

class Heston:
    def __init__(self, mu, rho, kappa, theta, xi):
        self.mu=mu
        self.rho=rho
        self.kappa=kappa
        self.theta=theta
        self.xi=xi


    def simulate(self, S0,v0, T,s_stop=None, v_stop=None, _seed=None):
        if _seed:
            np.random.seed(int(_seed))

        if s_stop is None:
            _s_stop = T
        else:
            _s_stop = s_stop

        if v_stop is None:
            _v_stop = T
        else:
            _v_stop = v_stop

        dt = 1/T
        MU = np.array([0, 0])
        COV = np.matrix([[1, self.rho], [self.rho, 1]])
        W = np.random.multivariate_normal(MU, COV, T)
        W_S = W[:, 0]
        W_v = W[:, 1]

        # Generate paths
        vt = np.zeros(T)
        vt[0] = v0
        St = np.zeros(T)
        St[0] = S0
        for t in range(1, T):
            if t>_v_stop:
                vt[t]=vt[t-1]
            else:
                vt[t] = np.abs(vt[t - 1] + self.kappa * (self.theta - vt[t - 1]) * dt + self.xi * np.sqrt(vt[t - 1]*dt) * W_v[t])
            #St[t] = St[t - 1] * np.exp((self.mu - 0.5 * vt[t - 1]) * dt + np.sqrt(vt[t - 1] * dt) * W_S[t])
            if t>_s_stop:
                St[t]=St[t-1]
            else:
                St[t] = St[t - 1] + St[t - 1]*self.mu* dt + St[t - 1]*np.sqrt(vt[t - 1] * dt)*W_S[t]


        return St, vt

#a = Heston(0.5,0.1,kappa=2,theta=0.15,xi = 0.2).simulate(100,0.15,20, _seed=4567,s_stop=10)
#aa = pd.DataFrame(list(a))
#pass