import tushare as ts
import datetime as dt
import numpy as np

class Universe:

    def __init__(self, tickers = ['601318','601155','000732','600340'], delay = 1, time = "2018-05-04"):

        self._tickers = tickers
        self._delay = delay
        self._update = dt.datetime.strptime(time, "%Y-%m-%d") - dt.timedelta(days = delay)
        self._networth = None
        # must run baseline to initialize
        self._index = None

    """
    Index classes currently not supported in tushare
    """

    def get_hs300(self):

        #ts.get_hs300s() #NOT WORKING!
        self._index = "hs300"
    
    def get_sz50(self):

        self._index = "sz50"

    def get_zz500(self):

        self._index = "399905"
    

    def baseline(self):
        
        start_ = str(self._update - dt.timedelta(days = 10))
        end_ = str(self._update)
        if self._index is None:
            prices = []
            for stock in self._tickers:
                prices.append(ts.get_hist_data(stock, start = start_, end = end_)["close"][0])
            indx = self.harmonicMean(prices)
        else:
            indx = ts.get_hist_data(self._index, start = start_, end = end_)["close"][0]
        # use harmonic mean as index unless some specific index type is provided
        if self._networth is None:
            self._networth = [1.]
        else:
            self._networth.append(indx / self._baseline)
        self._baseline = indx


    @staticmethod
    def harmonicMean(x):
        x = np.array(x)
        return 1/np.nanmean(1/x)


    def updatingNetWorth(self, time):

        self._update = dt.datetime.strptime(time, "%Y-%m-%d") - dt.timedelta(days = self._delay)
        self.baseline()

    
    def updatingPool(self, tickers, time):

        self._tickers = tickers
        self._update = dt.datetime.strptime(time, "%Y-%m-%d") - dt.timedelta(days = self._delay)
        

if __name__ == '__main__':

    tst = Universe()
    #print(tst.harmonicMean([1,2,3]))
    tst.baseline()
    tst.updatingNetWorth("2018-04-01")
    print(tst._networth)
