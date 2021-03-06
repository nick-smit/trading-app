import ccxt
import config
import pandas as pd

exchange = ccxt.binance({
    'apiKey': config.binance_api_key,
    'secret': config.binance_api_secret,
})

def getAvailableMarkets():
    markets = exchange.load_markets()

    return markets

def fetchCandles(symbol: str, timeframe:int, limit:int=30) -> pd.DataFrame:
    candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    
    return candlesToDataFrame(candles)

def candlesToDataFrame(candles) -> pd.DataFrame:
    df = pd.DataFrame(candles[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df