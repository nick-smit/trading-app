import pandas as pd
from exchange import getAvailableMarkets
import backtrader as bt
from os import path, mkdir
from datetime import datetime


def dataProvider(symbol, tf_in_minutes) -> pd.DataFrame:
    filename = f"./backtrading_data_{tf_in_minutes}/{symbol.replace('/', '')}.csv"

    df = pd.read_csv(filename, parse_dates=True)
    # df['datetime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')

    return df

def getSymbols():
    markets = getAvailableMarkets()
    
    symbols = []
    for market in markets:
        if market.split('/')[1] == 'EUR':
            symbols.append(market)
    
    return symbols

def saveResults(results, filename):
    dirname = './backtrading_results/'
    filename = f"{path.splitext(path.basename(filename))[0]}_{str(int(datetime.now().timestamp()))}.csv"
    if not path.isdir(dirname):
        mkdir(dirname)

    results.to_csv(dirname + filename)

class BaseStrat(bt.Strategy):
    def __init__(self):
        self.trades = []
        self.last_buy_order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED, Price: {order.price}")
                self.last_buy_order = order
            else:
                profit = abs(order.size) * order.price - self.last_buy_order.size * self.last_buy_order.price
                self.log(f"SELL EXECUTED, Price: {order.price}, Profit: {round(profit, 2)}")
                self.trades.append(
                    profit
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")
        
        self.order = None

    def log(self, txt):
        #print(txt)
        pass

    def stop(self):
        profitable_trades = [trade for trade in self.trades if trade > 0]

        success_rate = len(profitable_trades) / max(len(self.trades), 1)
        print(f"Made {len(self.trades)} trades, with a total sum of {sum(self.trades)}, success rate: {success_rate}")

        if len(self.trades) > 0:
            print(f"Best trade: {max(self.trades)}")
            print(f"Worst trade: {min(self.trades)}")

    def start(self):
        self.idx = 0

    def getDataframe(self, minCandles):
        columns = ['open','high', 'low', 'close', 'volume']

        self.idx += 1
        if (self.idx < minCandles):
            return pd.DataFrame([], columns=columns)

        # construct dataframe
        data = []
        for i in range(-(minCandles - 1), 0):
            data.append([self.data.open[i], self.data.high[i], self.data.low[i], self.data.close[i], self.data.volume[i]])

        return pd.DataFrame(data, columns=columns)