# -*- coding: utf-8 -*-
"""
@author: Kyle
"""

import numpy as np
import pandas as pd
import datetime as dt
import tushare as ts
import logging


class Alpha:

    def __init__(self, tickers, time, size = 10):

        self._logger = logging.getLogger(__name__)
        self._data = {}
        if isinstance(time, str):
            self._time = dt.datetime.strptime(time, "%Y-%m-%d")
        else:
            self._time = time
        self._universe = tickers
        # the initial pool
        self._size = size


    def get_data(self, time, source = "tushare"):

        # provide data for the scoring function
        for ticker in self._universe:
            if source == "tushare":
                self._data[ticker] = list(ts.get_hist_data(ticker, start = str(time), end = str(time + dt.timedelta(days = 1)), ktype = "5")["close"])
                # in tushare, with ktype="5" you get data BEFORE the end, while with ktype="D" you get data TILL the end. 
        self._logger.info('Loaded historical data, No. stocks %s' % (len(self._universe)))


    def scoring(self, time):

        # the algorithm part
        self._alpha = {}
        for ticker in self._universe:
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
            if ticker in self._universe:
                pool.append(ticker)
                i += 1
            if i >= self._size:
                break
        self._logger.info("On", str(self._time), 'selected tickers:', pool)
        return pool
            

    def main(self, ndays = 10):

        # for test
        import time
        from universe import Universe
        u = Universe(tickers = self._universe, time = self._time)
        
        for i in range(ndays):

            start_time = time.time()
            time_ = self._time + dt.timedelta(days = 1)
            print("On", time_) #############################
            self.get_data(time_)
            print("data ready, time used:", time.time() - start_time) ##############################
            start_time = time.time()
            self.scoring(time_)
            print("alpha, time used:", time.time() - start_time)
            print(self._alpha) ########################################
            if len(self._alpha) == 0:
                print("No alpha on this day")
                continue
            start_time = time.time()
            u.updatingPool(time_, self.selection())
            print("selection done, time used:", time.time() - start_time) #####################
            start_time = time.time()
            u.evaluation()
            print("evaluation done, time used:", time.time() - start_time) #####################
        
        return u._networth


if __name__ == '__main__':

    hs300 = list(pd.read_csv("hs300.csv", sep = " ", header = None, dtype = str)[0])
    hs300 = np.random.choice(hs300, size = 20, replace = False)
    time = dt.datetime.strptime("2018-05-02", "%Y-%m-%d")
    a = Alpha(hs300, time)
    out = a.main()
    print(out)
    
    
    
