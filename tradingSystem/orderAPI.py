# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 09:40:13 2018

@author: Kyle
"""

import numpy as np

class OrderApi:

    def __init__(self):

        self._slippage_std = .01
        self._prob_of_failure = .0001
        self._fee = .02
        self._fixed_fee = 10
        self._calculate_fee = lambda x : self._fee*abs(x) + self._fixed_fee

    def process_order(self, order):

        slippage = np.random.normal(0, self._slippage_std, size=1)[0]
        if np.random.choice([False, True], p=[self._prob_of_failure, 1 -self._prob_of_failure],size=1)[0]:
            trade_fee = self._fee*order[1]*(1+slippage)*order[2]
            return (order[0], order[1]*(1+slippage), order[2], self._calculate_fee(trade_fee))