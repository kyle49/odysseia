# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 14:21:20 2018

@author: Kyle
"""

import numpy as np
import pandas as pd
import datetime as dt
from tickDataProcessing import tickDataProcessing as TDP
from matplotlib import pyplot as plt

class estImpact:
    
    def __init__(self, stockID, path = None):
        
        self.DF = TDP(stockID, path)
        
        
    def _estExtraPrice(self, timeI):
        # DF is a TDP object
        # timeI is a time interval
        askbook = DF.askBook(timeI)
        frame = DF.get_data(timeI, ['totalAsk', 'meanAsk'])
        prices = askbook.columns.values
        amountOut = frame['totalAsk'] * frame['meanAsk'] - (prices * askbook).sum(axis = 1)
        volOut = frame['totalAsk'] - askbook.sum(axis = 1)
        self.askbook = askbook
        return amountOut / volOut
    
    
    def set_vars(self, targetVol, targetTime):
        self.timeInterval = targetTime
        self.vols = targetVol
    
    
    def main(self):
        exPList = self._estExtraPrice(self.timeInterval)
        frame = self.DF.get_data(self.timeInterval, ['vol', 'amount'])
        vwap = frame['vol'].sum() / frame['amount'].sum()
        inPList = self.askbook.mean()
        inPList = inPList[inPList.index >= vwap].cumsum()
        try:
            estPrice = inPList.index[sum(inPList <= self.vols)]
        except(IndexError):
            estPrice = exPList.mean()
        inflation = (estPrice - vwap) / vwap
        return estPrice, inflation


if __name__ == '__main__':

    DF = TDP('600519')
    df = DF.get_data(args = ['askbook'])

    import time
    start_ = time.time()
    
    res_full = tick_book(df)
    print(time.time() - start_)
    
    for i in range(10):     
        DF.sampling(jump = 10)
        out = DF.askBook(None)
        x = out.mean()
        plt.plot(x.cumsum())
    plt.show()
    
    
