# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 17:36:35 2018

@author: Kyle
"""

import numpy as np
#import pandas as pd
#import datetime as dt
from tickDataProcessing import tickDataProcessing as TDP
#from matplotlib import pyplot as plt

class estImpact:
    
    def __init__(self, stockID, path = None):
        self._DF = TDP(stockID, path)
        self._amts = [1e5]
        self._timeInterval = None
        self._ratio = 0
        self._method = 'TWAP'


    def set_times(self, targetTime):
        self._timeInterval = targetTime # a list of two or None
    
    
    def set_amts(self, targetAmount):
        if isinstance(targetAmount, float):
            self._amts = np.array([targetAmount])
            return
        self._amts = np.array(targetAmount)        
        
            
    def set_ratio(self, ratio):
        self._ratio = ratio
        # target vol X, market vol Y, ratio r
        # then the extra vol is X*X / (X + rY)
        # the larger r the better price we get
            
        
    def _estExtraPrice(self, timeI, ask = True):
        # DF is a TDP object
        # timeI is a time interval
        if ask:
            self._askbook = self._DF.askBook(timeI)
            frame = self._DF.get_data(timeI, ['totalAsk', 'meanAsk'])
            prices = self._askbook.columns.values
            amountOut = frame['totalAsk'] * frame['meanAsk'] - (prices * self._askbook).sum(axis = 1)
            volOut = frame['totalAsk'] - self._askbook.sum(axis = 1)
        else:
            self._bidbook = self._DF.bidBook(timeI)
            frame = self._DF.get_data(timeI, ['totalBid', 'meanBid'])
            prices = self._bidbook.columns.values
            amountOut = frame['totalBid'] * frame['meanBid'] - (prices * self._bidbook).sum(axis = 1)
            volOut = frame['totalBid'] - self._bidbook.sum(axis = 1)
        return amountOut / volOut
    
    
    def set_method(self, method):
        self._method = method
        # accept 'TWAP' or 'VWAP' for now
        
    
    def main(self, ask = True):
        exPList = self._estExtraPrice(self._timeInterval, ask)
        frame = self._DF.get_data(self._timeInterval, ['vol', 'amount'])
        if self._method == 'TWAP':
            exPrice = exPList.mean()
        elif self._method == 'VWAP':
            exPrice = sum(exPList * frame['vol']) / sum(frame['vol'])
        vol = frame['vol'].sum()
        volList = self._amts * self._amts / abs(self._amts + self._ratio * vol)
        vwap = frame['amount'].sum() / vol
        estPrice = []
        inflation = []
        if ask:
            inPList = self._askbook.mean()
            inPList = inPList[inPList.index >= vwap].cumsum()
            for _vol in volList:
                try:
                    _estPrice = inPList.index[sum(inPList <= _vol)]
                except(IndexError):
                    _estPrice = max(exPrice, _estPrice)
                print("Vol intended %d, estimated trading price %.2f" %(_vol, _estPrice))
                estPrice.append(_estPrice)
                inflation.append((_estPrice - vwap) / vwap)
        else:
            inPList = self._bidbook.mean()[::-1]
            inPList = inPList[inPList.index <= vwap].cumsum()
            for _vol in volList:
                try:
                    _estPrice = inPList.index[sum(inPList <= _vol)]
                except(IndexError):
                    _estPrice = min(exPrice, _estPrice)
                print("Vol intended %d, estimated trading price %.2f" %(_vol, _estPrice))
                estPrice.append(_estPrice)
                inflation.append((vwap - _estPrice) / vwap)
        return estPrice, inflation
    
    
if __name__ == '__main__':
    
    import datetime as dt
    out = estImpact('600519', path = 'dataPackages/')
    timeInterval = [dt.time(14), dt.time(14, 30)]
    out.set_times(timeInterval)
    volList = np.array([1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 1e6])
    out.set_amts(volList)
    out.set_method('VWAP')
    prices, infla = out.main(ask = False)
