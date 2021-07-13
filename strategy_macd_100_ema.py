from typing import Optional
from strategy_lib import BaseStrat, CandleTimeframe, Receipt, Position, Side
import pandas as pd
import pandas_ta as ta

class MACD100EmaStrat(BaseStrat):
    def GetCandleTimeframe(self) -> CandleTimeframe:
        return CandleTimeframe.TWELVE_HOUR

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
            return self._CheckSellCondition(last['close'], position)
            
        return None

    def OnTick(self, candle: dict, position: Position) -> Optional[Receipt]:
        if position.InPosition():
            return self._CheckSellCondition(candle['close'], position)

        return None

    def _CheckSellCondition(self, current_price: float, position: Position) -> Optional[Receipt]:
        if current_price < position.GetStoploss():
            return Receipt(Side.SELL)
        
        if current_price > position.GetTakeProfit():
            return Receipt(Side.SELL)

        return None
            
#BACKTESTING RESULTS:

# timeframe 30m
# Processing |################################| 26715/26715
# Took 0:03:22
# Wallet at end: 990.1178519151856
# Total trades: 694
# Success rate: 0.4899135446685879

# timeframe: 1h
# Processing |################################| 13283/13283
# Took 0:01:40
# Wallet at end: 1071.1279536971892
# Total trades: 349
# Success rate: 0.5501432664756447

# timeframe 2h
# Processing |################################| 6678/6678
# Took 0:00:51
# Wallet at end: 810.2662946975025
# Total trades: 156
# Success rate: 0.5705128205128205

# timeframe 4h
# Processing |################################| 3339/3339
# Took 0:00:25
# Wallet at end: 988.2818443563904
# Total trades: 101
# Success rate: 0.5841584158415841

if __name__ == '__main__':
    import exchange
    strat = MACD100EmaStrat()

    candles = exchange.fetchCandles('BTC/EUR', strat.GetCandleTimeframe().value, 101)

    pos = Position('BTC/EUR')
    order = strat.OnCandleClose(candles, pos)
    print(order)