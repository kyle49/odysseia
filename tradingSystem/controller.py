import datetime as dt
from algorithm01 import Algorithm_stalker as Algorithm
from domain import Portfolio
from orderAPI import OrderApi
from datasource import DataSource
from multiprocessing import Process, Queue
import logging

class Controller:

    def __init__(self, portfolio = None, algorithm = None):

        self._logger = logging.getLogger(__name__)
        self._portfolio = Portfolio() if portfolio is None else portfolio
        self._algorithm = Algorithm() if algorithm is None else algorithm
        self._order_api = OrderApi()

    @classmethod
    def backtest(cls, queue, controller = None):

        controller = cls() if controller is None else controller
        try:
            while True:
                if not queue.empty():
                    o = queue.get()
                    controller._logger.debug(o)

                    if o == 'POISON':
                        break
                    print(o)

                    timestamp = o[0]
                    ticker = o[1]
                    price = o[2]
                    vol = o[3]

                    # Update pricing

                    controller.process_pricing(ticker = ticker, price = price, vol = vol)

                    # Generate Orders

                    orders = controller._algorithm.generate_orders(ticker, timestamp, controller._portfolio)

                    # Process orders

                    if len(orders) > 0:                        
                        print("Orders", orders)
                        controller.process_order(orders)
                        controller._logger.info(controller._portfolio.value_summary(timestamp))

        except Exception as e:
            print(e)

        finally:
            controller._logger.info(controller._portfolio.value_summary(None))
            print("Day finished")


    def process_pricing(self, ticker, price, vol):

        self._portfolio.update(price=price, ticker = ticker)
        self._algorithm.update(stock=ticker, price = price, vol = vol)
        print("Pricing upgrade: done!")


    def process_order(self, order):

        success = False
        receipt = self._order_api.process_order(order) #(stockID, actual_price, vol, fees)
        if receipt is not None:
            success = self.process_receipt(receipt) 
        if order is None or success is False:
            self._logger.info(('{order_type} failed: %s at $%s for %s shares' % order).format(order_type = 'Sell' if order[2] < 0 else 'Buy'))
        #print("Order processing: done!")


    def process_receipt(self,receipt):

        ticker = receipt[0]
        price = receipt[1]
        share_delta = receipt[2]
        fee = receipt[3]
        temp = self._portfolio.balance - (price * share_delta + fee)

        if temp > 0:
            if share_delta < 0 and -share_delta > self._portfolio.get_shares(ticker):
                share_delta = -self._portfolio.get_shares(ticker)

            self._portfolio.update_trade(ticker=ticker, price=price, share_delta=share_delta, fee=fee)
            self._logger.debug('Trade on %s for %s shares at %s with fee %s' % (ticker,share_delta,price, fee))
            return True
        
        return False


from universe import Universe
from algorithm00 import Alpha

class Backtester:

    def __init__(self):

        self._logger = logging.getLogger(__name__)
        self._settings = {}
        self._default_settings = {
            
            'Source' : 'tushare',
            'Start_Day' : dt.datetime(2018,4,1),
            'End_Day' : dt.datetime.today(),
            'Tickers' : ['601318','601155','000732','600340'],
            'ktype' : 'D',
            'atype' : 'close',
            'Portfolio' : Portfolio(),
            'Algorithm' : Algorithm(),
        }


    def set_stock_universe(self, tickers):

        self._settings['Tickers'] = tickers

    """
    def set_portfolio(self, portfolio):

        self._settings['Portfolio'] = portfolio


    def set_algorithm(self, algorithm):

        self._settings['Algorithm'] = algorithm
    """

    def set_source(self, source):

        self._settings['Source'] = source


    def set_start_date(self, date):

        if isinstance(date, str):
            date = dt.datetime.strptime(date, "%Y-%m-%d")
        self._settings['Start_Day'] = date


    def set_end_date(self, date):

        if isinstance(date, str):
            date = dt.datetime.strptime(date, "%Y-%m-%d")
        self._settings['End_Day'] = date

    
    def set_freq_type(self, ktype):

        self._settings['ktype'] = ktype

    
    def set_arg_type(self, atype):

        self._settings['atype'] = atype


    def get_setting(self, setting):

        return self._settings[setting] if setting in self._settings else self._default_settings[setting]



    def backtest(self):

        #Setup Logger

        root = logging.getLogger()
        root.setLevel(level=logging.DEBUG)
        import os
        filepath = 'run.log'
        if os.path.exists(filepath):
            os.remove(filepath)
        root.addHandler(logging.FileHandler(filename=filepath))

        day_start = self.get_setting('Start_Day')
        day_end = self.get_setting('End_Day')
        day_current = day_start
        if day_current > day_end:
            print ("Error in time! Starting time > End time!!")
            return
        self._universe = Universe(tickers = self.get_setting('Tickers'), time = self.get_setting('Start_Day'))
        self._subuniverse = Universe(tickers = self.get_setting('Tickers'), time = self.get_setting('Start_Day'))
        self._portfolio = self.get_setting('Portfolio')
        self.set_stock_universe = Alpha(self.get_setting('Tickers'), day_current)

        while day_current < day_end:

            # Daily update

            day_current += dt.timedelta(days = 1)
            print(str(day_current)) #########################

            # Generate Alpha

            a = Alpha(self._universe._tickers, day_current)
            a.get_data(day_current)
            a.scoring(day_current)
            pool = a.selection()
            self._subuniverse.updatingPool(time = day_current, tickers = pool)
            self._algorithm = Algorithm()
            self._portfolio.set_quota(pool)

            # Multiprocess initialise
        
            q = Queue()
            ds = None
            c = None

            ds = DataSource(
                source=self.get_setting('Source'),
                start=self.get_setting('Start_Day'),
                end=self.get_setting('End_Day'),
                tickers=self.get_setting('Tickers'),
                ktype=self.get_setting('ktype'),
                atype=self.get_setting('atype')
            )

            c = Controller(
                portfolio=self._portfolio,
                algorithm=self._algorithm
            )
        
            p = Process(target=DataSource.process, args=((q,ds)))
            p1 = Process(target=Controller.backtest, args=((q,c)))

            p.start()
            p1.start()
            p.join()
            p1.join()
        

if __name__ == '__main__':

    import time
    import numpy as np
    import pandas as pd
    start_ = time.time()
    hs300 = list(pd.read_csv("hs300.csv", sep = " ", header = None, dtype = str)[0])
    hs300s = np.random.choice(hs300, size = 20, replace = False)
    b = Backtester()
    b.set_stock_universe(hs300s)
    b.set_start_date(dt.datetime(2018,5,3))
    b.set_end_date(dt.datetime(2018,5,8))
    b.set_source("tushare")
    b.set_freq_type("5")
    
    b.backtest()
    end_ = time.time()
    print("Total time used: ", end_ - start_)
