from fetch_backtrading_lib import *
from strategy_lib import CandleTimeframe
from sys import argv
import config

def fetchBacktradingData():
    symbols = getSymbls()
    if len(argv) == 2:
        fetchAllBacktradingData(config.markets, CandleTimeframe(argv[1]).GetInMinutes(), from_date='2021-01-01')
    else:
        for tf in CandleTimeframe:
            fetchAllBacktradingData(symbols, tf.GetInMinutes())

if __name__ == "__main__":
    fetchBacktradingData()
