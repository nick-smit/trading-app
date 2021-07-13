from typing import Optional
from strategy_lib import BaseStrat, CandleTimeframe, Receipt, Position, Side
import pandas as pd
import pandas_ta as ta

class MACD100EmaStrat(BaseStrat):
    def GetCandleTimeframe(self) -> CandleTimeframe:
        return CandleTimeframe.ONE_HOUR

    def GetMinCandles(self) -> int:
        return 101

    def OnCandleClose(self, df: pd.DataFrame, position: Position) -> Optional[Receipt]:
        df = df.join([ta.macd(df['close']), ta.ema(df['close'], 100)])

        last = df.iloc[-1]
        penultimate = df.iloc[-2]
        
        # todo implement resistance / support detection

        if not position.InPosition() and last['EMA_100'] < last['close']:
            if last['MACDs_12_26_9'] > last['MACD_12_26_9'] and penultimate['MACDs_12_26_9'] < penultimate['MACD_12_26_9']:
                stoploss = last['EMA_100']
                take_profit = last['close'] + ((last['close'] - last['EMA_100']) * 1.5)

                return Receipt(Side.BUY, stoploss=stoploss, take_profit=take_profit)
        elif position.InPosition():
            if last['close'] < position.GetStoploss():
                #sell if we hit stoplos (should be checked every tick/ minute)
                return Receipt(Side.SELL)
            
            if last['close'] > position.GetTakeProfit():
                #sell if we hit take profit (should be checked every tick/ minute)
                return Receipt(Side.SELL)
            
        return None

#BACKTESTING RESULTS:

# timeframe: 1h
# Processing |################################| 13283/13283
# Took 0:01:40
# Wallet at end: 1071.1279536971892
# Total trades: 349
# Success rate: 0.5501432664756447

if __name__ == '__main__':
    import exchange
    strat = MACD100EmaStrat()

    candles = exchange.fetchCandles('BTC/EUR', strat.GetCandleTimeframe().value, 101)

    pos = Position('BTC/EUR')
    order = strat.OnCandleClose(candles, pos)
    print(order)