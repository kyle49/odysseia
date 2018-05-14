# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 17:23:10 2018

@framework: http://srome.github.io/Build-Your-Own-Event-Based-Backtester-In-Python/
@author: Kyle
"""

class Portfolio:

    def __init__(self, balance=1000000):

        self._portfolio = {}
        self._portfolio['**CASH**'] = {'Shares' : balance, 'Price' : 1.0, 'Updates' : 1, 'Quota' : 0}
        self._quotaPerStock = 0
        # Initialised by set_quota

    def update(self, price, ticker):

        if ticker in self._portfolio:
            self._portfolio[ticker]['Price'] = price
            self._portfolio[ticker]['Updates'] = self._portfolio[ticker]['Updates'] + 1
        else:
            self._portfolio[ticker] = {}
            self._portfolio[ticker]['Price'] = price
            self._portfolio[ticker]['Shares'] = 0
            self._portfolio[ticker]['Quota'] = self._quotaPerStock
            self._portfolio[ticker]['Updates'] = 1


    @property
    def balance(self):

        return self._portfolio['**CASH**']['Shares']


    @balance.setter
    def balance(self, balance):

        self._portfolio['**CASH**']['Shares'] = balance


    def adjust_balance(self, delta):

        self._portfolio['**CASH**']['Shares'] = self.balance + delta


    def __contains__(self, item):

        return (item in self._portfolio)


    def value_summary(self, date):

        sum = self.get_total_value()
        return '%s : Stock value: %s, Cash: %s, Total %s' % (date, sum-self.balance, self.balance, sum)


    def get_total_value(self):

        sum = 0
        for stock in self._portfolio.values():
            sum += stock['Shares'] * stock['Price']
        return sum


    def get_value(self, ticker):

        return self.get_price(ticker) * self.get_shares(ticker)


    def get_price(self, ticker):

        return self._portfolio[ticker]['Price']


    def get_shares(self, ticker):

        if ticker not in self._portfolio:
            return -1
        return self._portfolio[ticker]['Shares']
    
    
    def get_quota(self, ticker):
        
        if ticker not in self._portfolio:
            return -1
        return self._portfolio[ticker]['Quota']


    def get_update_count(self, ticker):

        return self._portfolio[ticker]['Updates']


    def set_shares(self, ticker, shares):

        self._portfolio[ticker]['Shares'] = shares


    def set_quota(self, tickers):
        
        # Initialise
        quota = self.balance / len(tickers)
        self._quotaPerStock = quota
        for ticker in self._portfolio:
            if ticker in tickers:
                self._portfolio[ticker]['Quota'] = quota
            else:
                self._portfolio[ticker]['Quota'] = 0
                

    def update_shares(self, ticker, share_delta):

        self.set_shares(ticker, self.get_shares(ticker) + share_delta)
        self._portfolio[ticker]['Quota'] -= share_delta


    def update_trade(self, ticker, share_delta, price, fee):

        # Assumes negative shares are sells, requires validation from Controller
        self.set_shares(ticker, self.get_shares(ticker) + share_delta)
        self.adjust_balance(-(price*share_delta + fee))



    def __str__(self):

        return self._portfolio.__str__()


if __name__ == '__main__':

    p = Portfolio()
    out = p.get_total_value()
    print(out)
    print("Initial position")
    print(p._portfolio)
    ticker = "000000" # forged
    price = 10
    p.update(price, ticker)
    print("First update")
    print(p._portfolio)
    p.update(price, ticker)
    print("Second update")
    print(p._portfolio)
