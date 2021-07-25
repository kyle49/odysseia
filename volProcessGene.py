# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 13:28:22 2018

@author: Kyle
"""

import numpy as np
import scipy.stats as sts
import matplotlib.pyplot as plt
#import pandas as pd

class volSimu:
    
    def __init__(self, x, rate, Nrate, init = None):
        self.x = x # simulated independent price process
        self.init = init # dict. of prices - demands
        self.rate = rate # arrival rate of price dependent demands
        self.Nrate = Nrate # arrival rate of noise trades
        self.step = max(round(self.x[0] / 10000, 2), 0.01) # density of prices 
        
    def make_init(self, modifier, trend):
        self.init = {}
        inflow = np.random.poisson(modifier * self.rate)
        # distribute demands to each price
        for i in range(21):
            key_ = str(round(self.x[0] + self.step * (i - 10), 2))
            self.init[key_] = inflow * sts.binom.pmf(i, 20, trend)
    
    def simu_vol(self, trace = False, modifiers = [10, 3, 0.6], perHand = 100, Ptrend = 0.5):
        self.v = np.zeros(len(self.x)) 
        if self.init == None:
            self.make_init(modifier = modifiers[0], trend = Ptrend)
        if trace:
            print("Starting with: ", self.init)
        for i in range(len(self.x)):
            # volume traded = realised demand + noise trades
            if i == 0:
                self.v[i] = self.init[str(round(self.x[0], 2))]
                self.init[str(round(self.x[0], 2))] = 0
            else:
                if self.x[i - 1] <= self.x[i]:
                    list_ = np.arange(self.x[i - 1], self.x[i] + 0.001, self.step)
                else:
                    list_ = np.arange(self.x[i], self.x[i - 1] + 0.001, self.step)
                if trace:
                    print("Interation: ", i, " covered prices: ", list_)
                    print(self.init)
                for j in list_:
                    key_ = str(round(j, 2))
                    if key_ in self.init.keys():
                        self.v[i] += self.init[key_]
                        self.init[key_] = 0
            self.v[i] += np.random.poisson(self.Nrate)
            # Simulate new demand
            inflow = np.random.poisson(self.rate)
            if i / len(self.x) > 0.9 or i / len(self.x) < 0.1:
                inflow = np.random.poisson(self.rate * modifiers[1])
            if trace:
                print("Volume: ", self.v[i])
                print("New inflow: ", inflow)
            for j in range(21):
                key_ = str(round(self.x[i] + self.step * (j - 10), 2))
                if key_ in self.init.keys():
                    self.init[key_] = self.init[key_] * modifiers[2] + inflow * sts.binom.pmf(j, 20, Ptrend)
                else:
                    self.init[key_] = inflow * sts.binom.pmf(j, 21, 0.5)
        self.v = np.around(self.v) * perHand
        return self.v
    
    def bar_sum(self, w):
        mat = self.v.reshape((int(len(self.v) / w), w))
        return mat.sum(axis = 1)

if __name__=='__main__':
    
    Size = 4800
    sign_ = np.random.randint(2, size = Size) * 2 - 1
    prices = np.cumsum(np.random.poisson(1,Size) * 0.01 * sign_) + 10
    plt.plot(prices)
    plt.show()
    out = volSimu(prices, 10, 5)
    vols = out.simu_vol(modifiers = [10, 3, 0.6])
    vols_bar = out.bar_sum(120)
    plt.plot(vols_bar)
    plt.show()
