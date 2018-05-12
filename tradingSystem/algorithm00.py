# -*- coding: utf-8 -*-
"""
@author: Kyle
"""

import numpy as np
import pandas as pd
import datetime as dt
import tushare as ts
import logging
from universe import Universe

class Alpha:

    def __init__(self, tickers, time, size = 10):

        self._logger = logging.getLogger(__name__)
        self._data = {}
        if isinstance(time, str):
            self._time = dt.datetime.strptime(time, "%Y-%m-%d")
        else:
            self._time = time
        self._universe = Universe(tickers, time)
        # Trivial or follow a certain index
        self._subuniverse = Universe(tickers, time)
        # The main objective of this class
        self._size = size


    def get_data(self, time, source = "tushare"):

        # provide data for the scoring function
        for ticker in self._universe._tickers:
            if source == "tushare":
                self._data[ticker] = list(ts.get_hist_data(ticker, start = str(time), end = str(time + dt.timedelta(days = 1)), ktype = "5")["close"])
                # in tushare, with ktype="5" you get data BEFORE the end, while with ktype="D" you get data TILL the end. 
        self._logger.info('Loaded historical data, No. stocks %s' % (len(self._universe._tickers)))


    def scoring(self, time):

        # the algorithm part
        self._alpha = {}
        for ticker in self._universe._tickers:
            if len(self._data[ticker]) == 0:
                continue
            self._alpha[ticker] = np.mean(self._data[ticker]) - self._data[ticker][0]
            # TWAP - close
        self._time = time
        self._logger.info('Computation of alphas completed')
            

    def selection(self):

        aaa = pd.DataFrame(list(self._alpha.items())).sort_values(1)
        i = 0
        pool = []
        for row in aaa.iterrows():
            ticker = row[1][0]
            if ticker in self._universe._tickers:
                pool.append(ticker)
                i += 1
            if i >= self._size:
                break
        self._subuniverse.updatingPool(time = self._time, tickers = pool)
        self._logger.info('On', str(self._subuniverse._update), 'selected tickers:', self._subuniverse._tickers)
        return self._subuniverse._tickers
            

    def main(self, ndays = 10):

        # for test
        import time
        
        for i in range(ndays):

            start_time = time.time()
            time_ = self._time + dt.timedelta(days = i)
            print("On", time_) #############################
            self.get_data(time_)
            stop_time = time.time()
            print("data ready, time used:", time.time() - start_time) ##############################
            start_time = time.time()
            self.scoring(time_)
            print("alpha, time used:", time.time() - start_time)
            print(self._alpha) ########################################
            if len(self._alpha) == 0:
                print("No alpha on this day")
                continue
            start_time = time.time()
            self.selection()
            self._universe.updatingPool(time_)
            print("selection done, time used:", time.time() - start_time) #####################
            start_time = time.time()
            self._universe.evaluation()
            self._subuniverse.evaluation()
            print("evaluation done, time used:", time.time() - start_time) #########################


if __name__ == '__main__':

    sz50 = list(pd.read_csv("sz50.csv", sep = " ", header = None, dtype = str)[0])
    time = dt.datetime.strptime("2018-04-23", "%Y-%m-%d")
    a = Alpha(sz50, time)
    print(a._universe._tickers)
    a.main()
    print(a._subuniverse._networth)
    print(a._universe._networth)
    
