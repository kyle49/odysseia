# -*- coding: utf-8 -*-
"""
@author: Kyle
"""

import tushare as ts
import datetime as dt
import numpy as np
import pandas as pd

class Universe:

    """
    Management of the pool
    """


    def __init__(self, tickers = ['601318','601155','000732','600340'], time = "2018-05-02", delay = 1, index_type = None):

        self._tickers = tickers
        if isinstance(time, str):
            self._update = dt.datetime.strptime(time, "%Y-%m-%d")
        else:
            self._update = time
        
        self._delay = delay
        # action on delay 1 and evaluation of performance on delay 2
        self._networth = [1.]
        # must run baseline to initialize
        self._index = index_type
        # only accept "hs300", "sz50" and "399905" for "zz500"


    def updatingPool(self, time, tickers = None):

        if tickers is not None:
            self._tickers = tickers
        if isinstance(time, str):
            time = dt.datetime.strptime(time, "%Y-%m-%d")
        self._update = time


    def evaluation(self):
        
        """
        If the pool is not from an index, compare harmonic mean, use index otherwise.
        """

        if self._index is None:
            out = self.find_next_data(self._update)
            if out is None:
                return 1
            prices = []
            for stock in self._tickers:
                try:
                    p_ = ts.get_hist_data(stock, start = str(self._update), end = str(out[0]))["close"]
                except Exception as e:
                    continue
                if len(p_) != 0:
                    prices.append(p_[0])
            if len(prices) == 0:
                print("No data on the next day, unable to update")
                return 1
            indx = self.harmonicMean(prices)
            out_ = self.find_next_data(out[0])
            if out_ is None:
                return 1
            prices = []
            for stock in self._tickers:
                try:
                    p_ = ts.get_hist_data(stock, start = str(out[0]), end = str(out_[0]))["close"]
                except Exception as e:
                    continue
                if len(p_) != 0:
                    prices.append(p_[0])
            if len(prices) == 0:
                print("No data on the next day, unable to update")
                return 1
            self._networth.append(self.harmonicMean(prices) / indx)
        else:
            out = self.find_next_data(self._update, index_type = self._index)
            if out is None:
                return 1
            out_ = self.find_next_data(out[0], index_type = self._index)
            if out_ is None:
                return 1
            self._networth.append(out_[1] / out[1])    

        return 0


    @staticmethod
    def find_next_data(time, index_type = "hs300"):
        if isinstance(time, str):
            time = dt.datetime.strptime(time, "%Y-%m-%d")
        p = pd.Series()
        attempt = 1
        while len(p) == 0:
            time_ = time + dt.timedelta(days = attempt)
            # print("try: ", time, time_) ########################
            p = ts.get_hist_data(index_type, start = str(time), end = str(time_))["close"]
            attempt += 1
            if attempt > 9:
                print("Unable to find new data")
                return None
        return time_, p[0]


    @staticmethod
    def harmonicMean(x):
        x = np.array(x)
        return 1/np.nanmean(1/x)


    

        

if __name__ == '__main__':

    tst = Universe()
    tickers = ['601318','601155','000732','600340']
    #out = tst.find_next_data(tst._update)
    #print(out)
    #print(ts.get_hist_data("hs300", "2018-05-03", "2018-05-04")["close"])
    tst.updatingPool("2018-05-03", tickers)
    tst.evaluation()
    tst.updatingPool("2018-05-04", tickers)
    tst.evaluation()
    print(tst._networth)


