import pandas as pd
import pandas_ta as ta

def calculate(df: pd.DataFrame, long_sma_period:int=20, short_sma_period:int=5) -> pd.DataFrame:
    # df['sma_long'] = df['close'].rolling(window=long_sma_period).mean()
    # df['sma_short'] = df['close'].rolling(window=short_sma_period).mean()

    bbands = ta.bbands(df['close'])
    df = df.join(bbands)

    # df['bbands_diff'] = df['BBU_5_2.0'] - df['BBL_5_2.0']
    # df['bbands_diff_percent'] = df['bbands_diff'] / df['close'] 
    return df

def make_decision(in_position, df):
    current = len(df.index) - 1
    previous = len(df.index) - 2

    if not in_position and df['BBL_5_2.0'][current] > df['close'][current] and df['BBL_5_2.0'][previous] < df['close'][previous]:
        return 'buy'
    elif in_position and df['BBM_5_2.0'][current] < df['close'][current]:
        return 'sell'
    
    return 'hold'


if __name__ == '__main__':
    import exchange

    candles = exchange.fetchCandles('DOGE/EUR', '1h', 30)
    df = exchange.candlesToDataFrame(candles)

    res = calculate(df)
    print(res)