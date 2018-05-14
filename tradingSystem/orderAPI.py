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

    """
    def process_order_simu(self, order):

        # takes an order = [stockID, price, vol] from the algorithm class
        slippage = np.random.normal(0, self._slippage_std, size=1)[0]
        if np.random.choice([False, True], p=[self._prob_of_failure, 1 -self._prob_of_failure],size=1)[0]:
            return (order[0], order[1]*(1+slippage), order[2], self._calculate_fee(order))
        # return (stockID, actual_price, vol, fees)
    """


    def process_order(self, order):

        # takes a tuple, return a tuple
        return (order[0], order[1], order[2], self._calculate_fee(order))


    @staticmethod
    def _calculate_fee(order):

        short = 0
        if order[2] < 0:
            order[2] = -order[2]
            short = 1
        fee = max(1, np.round(order[2]/1000, 0)) + max(5, order[1] * order[2] * (.003 + .001 * short))
        return fee


if __name__ == "__main__":

    a = OrderApi()
    order1 = ["A", 10, 1000]
    order2 = ["B", 8, -400]
    print(a.process_order(order1))
    print(a.process_order(order2))