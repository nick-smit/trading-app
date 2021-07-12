import pandas as pd
import strategy_long_short_sma_crossing_v2
import backtrader as bt
from backtrader_lib import *

tf_in_minutes = 60

class Strat(BaseStrat):
    params=(
        ('short_sma', 5),
        ('long_sma', 20),
    )

    def next(self):
        df = self.getDataframe(self.params.long_sma + 2)
        if df.empty:
            return
        
        in_position = bool(self.position)
        df = strategy_long_short_sma_crossing_v2.calculate(df, self.params.long_sma, self.params.short_sma)
        
        decision = strategy_long_short_sma_crossing_v2.make_decision(in_position, df)
        
        if decision == 'buy':
            self.buy(price=self.data.close[0])
        elif decision == 'sell':
            self.close(price=self.data.close[0])


if __name__ == '__main__':
    symbols = getSymbols()

    results = pd.DataFrame(columns=['symbol', 'result value'])
    
    for symbol in symbols:
        df = dataProvider(symbol, tf_in_minutes)

        cerebro = bt.Cerebro()

        data = bt.feeds.PandasData(dataname=df, open='open', high='high', low='low', close='close', volume='volume', datetime='datetime', openinterest=None)
        cerebro.adddata(data)

        cerebro.addstrategy(Strat, short_sma=7, long_sma=21)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

        cerebro.broker.set_cash(100000)

        # Print out the starting conditions
        print(f"Starting {symbol} portfolio value: {cerebro.broker.getvalue()}")

        # Run over everything
        cerebro.run()

        # Print out the final result
        print(f"Result {symbol} portfolio value: {cerebro.broker.getvalue()}")
        results.loc[len(results)] = [symbol, round(cerebro.broker.getvalue(), 2)]

    print(results)
    saveResults(results, __file__)