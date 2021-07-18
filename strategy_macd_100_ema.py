from typing import Optional
from strategy_lib import BaseStrat, CandleTimeframe, Receipt, Position, Side
import pandas as pd
import pandas_ta as ta
from time import time

version = int(time())

class MACD100EmaStrat(BaseStrat):
    def GetCandleTimeframe(self) -> CandleTimeframe:
        return CandleTimeframe.ONE_HOUR

    def GetMinCandles(self) -> int:
        return 101

    def OnCandleClose(self, df: pd.DataFrame, position: Position) -> Optional[Receipt]:
        ema_length = 100
        ema_key = 'EMA_' + str(ema_length)
        df = df.join([ta.macd(df['close']), ta.ema(df['close'], ema_length)])

        last = df.iloc[-1]
        penultimate = df.iloc[-2]
        # todo implement resistance / support detection

        if not position.InPosition() and last[ema_key] < last['close']:
            if last['MACDs_12_26_9'] > last['MACD_12_26_9'] and penultimate['MACDs_12_26_9'] < penultimate['MACD_12_26_9']:
                stoploss = last[ema_key]
                take_profit = last['close'] + ((last['close'] - last[ema_key]) * 1.5)

                # last check before buying, can we make more than 0.5% with this trade? If not, we should not trade...
                take_profit_percent = take_profit / last['close']
                if take_profit_percent > 1.005:
                    return Receipt(Side.BUY, stoploss=stoploss, take_profit=take_profit)
        elif position.InPosition():
            if last['close'] < position.GetStoploss():
                return Receipt(Side.SELL)
            
            if last['close'] > position.GetTakeProfit():
                # Nice, but is the momentum getting stronger?
                last_five = df.tail(5)
                for index in last_five.head(4).index:
                    if last_five['MACDh_12_26_9'][index] > last_five['MACDh_12_26_9'][index + 1]:
                        # sell if bullish momentum is not getting stringer for 5 candles in a row
                        return Receipt(Side.SELL)
            
        return None
            
#BACKTESTING RESULTS:

# timeframe: 1h
# Processing |********************************| 0 minutes remaining
# Took 0:02:12
# Wallet at end: 
# EUR: 1119.8779377958317
# ETH: 0.0
# BTC: 0.0
# BNB: 0.0
# DOGE: 0.0
# XRP: 0.0
# Total trades: 407
# Success rate: 0.515970515970516

if __name__ == '__main__':
    import exchange
    strat = MACD100EmaStrat()

    candles = exchange.fetchCandles('BTC/EUR', strat.GetCandleTimeframe().value, 101)

    pos = Position('BTC/EUR')
    order = strat.OnCandleClose(candles, pos)
    print(order)