# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 09:42:00 2018

@author: Kyle
"""

import numpy as np
import pandas as pd
import tushare as ts
import datetime as dt
import logging
import os


class DataSource:

    '''
    Data source for the backtester. Must implement a "get_data" function
    which streams data from the data source.
    '''

    def __init__(self, source='tushare', tickers=['601318'], start = dt.datetime(2018,1,1), end=dt.datetime.today(), ktype="D", atype = "close"):

        self._logger = logging.getLogger(__name__)
        self.set_source(source = source, tickers = tickers, start = start, end = end, ktype = ktype, atype = atype)


    @classmethod
    def process(cls, queue, source = None):

        # takes queue from controller, add data to the queue
        source = cls() if source is None else source
        while True:
            data = source.get_data()
            if data is not None:
                queue.put(data)
                if data == 'POISON': 
                    # POISON is set to kill process
                    break
    

    def set_source(self, source, tickers, start, end, ktype = "D", atype = "close"):

        prices = pd.DataFrame()
        volume = pd.DataFrame()
        counter = 0.
        if source == 'tushare':
            for ticker in tickers:
                try:
                    self._logger.info('Loading ticker %s' % (counter / len(tickers)))
                    df = ts.get_hist_data(ticker, start = str(start), end = str(end), ktype = ktype)[[atype, "volume"]]
                    prices[ticker] = df.iloc[::-1, 0]
                    volume[ticker] = df.iloc[::-1, 1]         
                except Exception as e:
                    self._logger.error(e)
                    pass
                counter += 1

            events = []
            for i in range(len(prices)):
                timestamp = dt.datetime.strptime(prices.index[i], "%Y-%m-%d %H:%M:%S")
                for k in range(len(prices.iloc[i, :])):
                    if np.isfinite(prices.iloc[i, k] * volume.iloc[i, k]):
                        events.append((timestamp, prices.columns[k], prices.iloc[i, k], volume.iloc[i, k]))
        
        if source == 'local':
            # only for tick 3s data on each day
            path = "/dataDisc/dataCenter/readwrite_mass/tickdata/ticks/"
            if isinstance(end, str):
                end = dt.datetime.strptime(end, "%Y-%m-%d")
            path += str(end.year) + os.sep + self.convert_to_str(end.month) + os.sep + str(end.year) + self.convert_to_str(end.month) + self.convert_to_str(end.day) + os.sep
            for ticker in tickers:
                try:
                    self._logger.info('Loading ticker %s' % (counter / len(tickers)))
                    filename = path + ticker + ".csv"
                    print("Path: ", filename)
                    df = pd.read_csv(filename, header = None, sep = " ")
                    aaa = sum(df.iloc[:,0] < 93000000)
                    df.drop(np.arange(aaa), inplace = True)
                    data_ = df.iloc[:,[3,10]]
                    data_.index = df[0].apply(self.convert_to_time)
                    prices[ticker] = data_.iloc[:,1]
                    volume[ticker] = data_.iloc[:,0]
                except Exception as e:
                    self._logger.error(e)
                    pass
                counter += 1

            events = []
            for i in range(len(prices)):
                timestamp = prices.index[i]
                for k in range(len(prices.iloc[i, :])):
                    if np.isfinite(prices.iloc[i, k] * volume.iloc[i, k]):
                        events.append((timestamp, prices.columns[k], prices.iloc[i, k], volume.iloc[i, k]))

        self._source = events
        self._logger.info('Loaded data!')


    @staticmethod
    def convert_to_str(x):
        if x < 10:
            return ("0" + str(x))
        else:
            return str(x)


    @staticmethod
    def convert_to_time(times):
	    return dt.time( int(times//1e7), int(times%1e7//1e5), int(times%1e5//1e3))


    def get_data(self):

        try:
            return self._source.pop(0)
        except IndexError as e:
            return 'POISON'


if __name__ == '__main__':

    import time

    start_ = time.time()
    ds = DataSource(
            source='tushare',
            start=dt.datetime(2018,5,10),
            end=dt.datetime.today(),
            tickers=['601318'],
            ktype="5"
        )

    out = ds.get_data()
    print(ds._source[0:10])
    end_ = time.time()
    print("Time used: ", end_ - start_)
    """
    start_ = time.time()
    ds = DataSource(
            source='local',
            start=dt.datetime(2018,5,1),
            end="2018-05-03",
            tickers=['601318'],
            ktype="5"
        )

    out = ds.get_data()
    print(ds._source[0:10])
    end_ = time.time()
    print("Time used: ", end_ - start_)
    """