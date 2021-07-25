# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 16:12:30 2018

@author: Kyle
"""

import numpy as np

class gridTrade:
    
    def __init__(self, base = None, 
                 grid = None, gridUp = None, gridDown = None, 
                 UB = np.inf, LB = 0,
                 longFee = .0005, shortFee = .0005):
        self._base = base
        self._gridUp = grid
        if gridUp is not None:
            self._gridUp = gridUp
        self._gridDown = grid
        if gridDown is not None:
            self._gridDown = gridDown
        self._UB = UB
        self._LB = LB
        self._longFee = longFee
        self._shortFee = shortFee
        self._maxTrade = 5 # maximum number of trades per tick of time
        
    def initPortfolio(self, cash, position, baseVol):
        self.Cash = cash
        self.Portfolio = position
        self._baseVol = baseVol
        
    def dVol(self):
        return self._baseVol # Vol per hand is fixed
        
    def long(self):
        amount = self.dVol() * self.currentPrice * (1 + self._longFee)
        if self.Cash >= amount:
            self.Cash -= amount
            self.Portfolio += self.dVol()
            print("Buy succuess at price %.2f, current position: %d, current cash: %.2f"
                  %(self.currentPrice, self.Portfolio, self.Cash))
        else:
            dVol = round(self.Cash / ((1 + self._longFee) * self.currentPrice))
            self.Cash = 0
            self.Portfolio += dVol
            print("Cash depleted, %d shares are actually traded instead of intended %d shares at price %.2f"
                  %(dVol, self.dVol(), self.currentPrice))
            
    def short(self, longOnly = True):
        if longOnly:
            if self.Portfolio > self.dVol():
                self.Portfolio -= self.dVol()
                self.Cash += self.currentPrice * self.dVol() * (1 - self._shortFee)
                print("Sell succuess at prices %.2f, current position: %d, current cash: %.2f"
                      %(self.currentPrice, self.Portfolio, self.Cash))
            else:
                self.Cash += self.currentPrice * self.Portfolio * (1 - self._shortFee)
                print("Shares depleted, the remaining %d shares sold instead of intended %d shares at price %.2f"
                      %(self.Portfolio, self.dVol(), self.currentPrice))
                self.Portfolio = 0
        else:
            self.Portfolio -= self.dVol()
            self.Cash += self.currentPrice * self.dVol() * (1 - self._shortFee)
        
    def run(self, Ts, base = None):
        if base is None:
            if self._base is None:
                base = Ts[0]
            else:
                base = self._base
        for i in range(len(Ts)):
            self.currentPrice = Ts[i]
            count = 0
            while Ts[i] > base + self._gridUp and Ts[i] <= self._UB:
                self.short()
                base += self._gridUp
                count += 1
                if count >= 5:
                    print("Maximum number of trades reached, stop buying")
                    break
            while Ts[i] < base - self._gridDown and Ts[i] >= self._LB and count < self._maxTrade:
                self.long()
                base -= self._gridDown
                count += 1
                if count >= 5:
                    print("Maximum number of trades reached, stop selling")
                    break
                
    def Summary(self, printOut = False):
        netWorth = self.Cash + self.Portfolio * self.currentPrice * (1 - self._shortFee)
        if printOut:
            print("Position: %d, cash: %.2f, net worth: %.2f"
                  %(self.Portfolio, self.Cash, netWorth))
        else:
            return netWorth
            
    def run_analysis(self, Ts, base = None):
        NetWorth = []
        stockRet = [0]
        if base is None:
            if self._base is None:
                base = Ts[0]
            else:
                base = self._base
        for i in range(len(Ts)):
            self.currentPrice = Ts[i]
            if i > 0:
                stockRet.append(self.Portfolio * (Ts[i] - Ts[i-1]))
            count = 0
            while Ts[i] > base + self._gridUp and Ts[i] <= self._UB:
                self.short()
                base += self._gridUp
                count += 1
                if count >= 5:
                    print("Maximum number of trades reached, stop selling")
                    break
            while Ts[i] < base - self._gridDown and Ts[i] >= self._LB and count < self._maxTrade:
                self.long()
                base -= self._gridDown
                count += 1
                if count >= 5:
                    print("Maximum number of trades reached, stop buying")
                    break
            NetWorth.append(self.Summary())
        return NetWorth, stockRet
    
    
if __name__ == "__main__":
    
    import pandas as pd
    from matplotlib import pyplot as plt
    
    _simus = np.random.normal(size = 100)
    dp = pd.Series(np.exp(_simus / 5))
    plt.plot(dp.cumprod())
    plt.show()
    simuPrices = 30 + dp.cumprod() * 0.4
    plt.plot(simuPrices)
    plt.title("Simulated prices")
    plt.show()
    
    algo1 = gridTrade(base = 32,
                      grid = .05,
                      UB = 33, LB = 31)
    algo1.initPortfolio(cash = 1000000, position = 0, baseVol = 1000)
    worth, rets = algo1.run_analysis(Ts = simuPrices)
    algo1.Summary(printOut = True)

    algo2 = gridTrade(base = 32,
                      grid = .2,
                      UB = 33, LB = 31)
    algo2.initPortfolio(cash = 1000000, position = 0, baseVol = 1000)
    worth, rets = algo2.run_analysis(Ts = simuPrices)
    algo2.Summary(printOut = True)
