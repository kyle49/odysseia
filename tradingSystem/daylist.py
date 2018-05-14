import datetime as dt


def find_next_trading_day(time):

    # April and May in 2018

    start_time = dt.datetime(2018, 4, 14)
    end_time = dt.datetime(2018, 5, 14)

    d = []

    while start_time < end_time:

        d.append(start_time)
        start_time = start_time + dt.timedelta( days = 1 )

    holidays = [0, 1, 7, 8, 14, 15, 16, 17, 21, 22, 28, 29]

    i = 0

    for i in range(len(d)):
        if d[i] > time and i not in holidays:
            return d[i]

    print("No more vaild day!")
    return None

if __name__ == '__main__':

    print(find_next_trading_day(dt.datetime(2018, 5, 1)))
    print(find_next_trading_day(dt.datetime(2018, 5, 5)))
        
    

     
