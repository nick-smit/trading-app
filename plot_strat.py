import plotly.graph_objects as go
import pandas as pd
from strategy_supertrend import calculate

df = pd.read_csv('./backtrading_data_60/BTCEUR.csv')
df = df.iloc[len(df) - 100:]
df = df.reset_index()

df = calculate(df)

fig = go.Figure(data=[go.Candlestick(x=df['datetime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])

fig.add_trace(
    go.Line(
        x=df['datetime'],
        y=df['upperband']
    )
)

fig.add_trace(
    go.Line(
        x=df['datetime'],
        y=df['lowerband']
    )
)

fig.show()