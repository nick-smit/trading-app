import pandas as pd
import talib

#temp
import warnings
warnings.filterwarnings('ignore')

def calculate(df: pd.DataFrame, period:int=7, atr_multiplier:int=3) -> pd.DataFrame:
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], period)
    
    hl2 = (df['high'] + df['low']) / 2
    atr_multiplied = df['atr'] * atr_multiplier
    df['upperband'] = hl2 + atr_multiplied
    df['lowerband'] = hl2 - atr_multiplied

    df['in_uptrend'] = True
    for current in range(1, len(df.index)):
        previous = current - 1
        
        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]

    return df

def make_decision(in_position, df):
    current = len(df.index) - 1
    previous = current - 1

    if not in_position and not df['in_uptrend'][previous] and df['in_uptrend'][current]:
        return 'buy'
    elif in_position and df['in_uptrend'][previous] and not df['in_uptrend'][current]:
        return 'sell'
    
    return 'hold'
