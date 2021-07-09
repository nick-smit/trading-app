import pandas as pd
import config
import strategy_long_short_sma_crossing
import backtrader as bt

tf_in_minutes = 60

markets = []
for market in config.markets:
    if market == 'BTC/EUR':
        markets.append({'symbol': market, 'in_position': False})

def dataProvider(symbol) -> pd.DataFrame:
    filename = f"./backtrading_data_{tf_in_minutes}/{symbol.replace('/', '')}.csv"

    df = pd.read_csv(filename, parse_dates=True)
    # df['datetime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')

    return df

class SupertrendStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        #dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
        pass

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
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
                self.log(f"SELL EXECUTED, Price: {order.price}")
                self.trades.append(
                    abs(order.size) * order.price - self.last_buy_order.size * self.last_buy_order.price
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")
        
        self.order = None

    def start(self):
        self.idx = 0

    def stop(self):
        profitable_trades = [trade for trade in self.trades if trade > 0]
        print(profitable_trades[0])
        success_rate = len(profitable_trades) / len(self.trades)
        print(f"Made {len(self.trades)} trades, with a total sum of {sum(self.trades)}, success rate: {success_rate}")

    def next(self):
        self.idx += 1
        if (self.idx < 30):
            return

        # construct dataframe
        data = []
        for i in range(-29, 0):
            data.append([self.data.open[i], self.data.high[i], self.data.low[i], self.data.close[i], self.data.volume[i]])
            
        df = pd.DataFrame(data, columns=['open','high', 'low', 'close', 'volume'])
        
        in_position = bool(self.position)
        df = strategy_long_short_sma_crossing.calculate(df)
        
        decision = strategy_long_short_sma_crossing.make_decision(in_position, df)
        
        if decision == 'buy':
            self.buy(price=self.data.close[0])
        elif decision == 'sell':
            self.close(price=self.data.close[0])


if __name__ == '__main__':
    for symbol in config.markets:
        df = dataProvider(symbol)

        cerebro = bt.Cerebro()

        data = bt.feeds.PandasData(dataname=df, open='open', high='high', low='low', close='close', volume='volume', datetime='datetime', openinterest=None)
        cerebro.adddata(data)

        cerebro.addstrategy(SupertrendStrategy)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

        cerebro.broker.set_cash(100000)

        # Print out the starting conditions
        print(f"Starting {symbol} portfolio value: {cerebro.broker.getvalue()}")

        # Run over everything
        cerebro.run()

        # Print out the final result
        print(f"Result {symbol} portfolio value: {cerebro.broker.getvalue()}")