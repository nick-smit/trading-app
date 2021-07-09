import pandas as pd
import exchange
from helpers import log
import strategy_long_short_sma_crossing
from bot_lib import *

def check_buy_or_sell_signal(market: dict, df: pd.DataFrame):
    decision = strategy_long_short_sma_crossing.make_decision(market['in_position'], df)

    if decision == 'buy':
        market['in_position'] = buy(market['symbol'], market['max_decimals'])
    elif decision == 'sell':
        market['in_position'] = not sell(market['symbol'])

markets = getMarkets()

def bot_long_short_sma_crossing():
    log("Checking markets", False)
    for i in range(len(markets)):
        market = markets[i]
        if (market['symbol'] != 'BTC/EUR'):
            continue

        candles = None
        try:
            candles = exchange.fetchCandles(market['symbol'])
        except Exception as e:
            log(f"Got exception: {e}")
            continue

        df = strategy_long_short_sma_crossing.calculate(candles)

        check_buy_or_sell_signal(markets[i], df)
