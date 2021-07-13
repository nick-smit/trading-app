from typing import Optional
import pandas as pd
from strategy_lib import BaseStrat, CandleTimeframe, Position, Receipt, Side

def calculate(df: pd.DataFrame, long_sma_period:int=20, short_sma_period:int=5) -> pd.DataFrame:
    df['sma_long'] = df['close'].rolling(window=long_sma_period).mean()
    df['sma_short'] = df['close'].rolling(window=short_sma_period).mean()

    return df

def make_decision(in_position, df):
    current = len(df.index) - 1
    previous = current - 1

    if not in_position and df['sma_short'][current] > df['sma_long'][current] and df['sma_short'][previous] < df['sma_long'][previous]:
        return 'buy'
    elif in_position and df['sma_short'][current] < df['sma_long'][current]:
        return 'sell'
    
    return 'hold'

class LongShortSMACrossing(BaseStrat):
    def GetCandleTimeframe(self) -> CandleTimeframe:
        return CandleTimeframe.ONE_HOUR
    
    def GetMinCandles(self) -> int:
        return 21

    def OnCandleClose(self, candles: pd.DataFrame, position: Position) -> Optional[Receipt]:
        df = calculate(candles)
        decision = make_decision(position.InPosition(), df)
        
        if decision == 'buy':
            return Receipt(Side.BUY)
        elif decision == 'sell':
            return Receipt(Side.SELL)
        
        return None

#BACKTESTING RESULTS:

# timeframe: 1h
# Processing |################################| 13283/13283
# Took 0:01:25
# Wallet at end: 809.4669980217993
# Total trades: 1398
# Success rate: 0.4034334763948498

if __name__ == '__main__':
    import exchange
    strat = LongShortSMACrossing()

    candles = exchange.fetchCandles('BTC/EUR', strat.GetCandleTimeframe().value, 101)

    pos = Position('BTC/EUR')
    order = strat.OnCandleClose(candles, pos)
    print(order)