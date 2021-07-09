import pandas as pd

def calculate(df: pd.DataFrame, long_sma_period:int=20, short_sma_period:int=5) -> pd.DataFrame:
    df['sma_long'] = df['close'].rolling(window=long_sma_period).mean()
    df['sma_short'] = df['close'].rolling(window=short_sma_period).mean()

    return df

def make_decision(in_position, df):
    current = len(df.index) - 1

    if not in_position and df['sma_short'][current] > df['sma_long'][current]:
        return 'buy'
    elif in_position and df['sma_short'][current] < df['sma_long'][current]:
        return 'sell'
    
    return 'hold'
