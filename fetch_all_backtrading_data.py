from fetch_backtrading_lib import *
from strategy_lib import CandleTimeframe
from sys import argv

def fetchBacktradingData():
    symbols = getSymbls()
    if len(argv) == 2:
        fetchAllBacktradingData(symbols, CandleTimeframe(argv[1]).GetInMinutes())
    else:
        for tf in CandleTimeframe:
            fetchAllBacktradingData(symbols, tf.GetInMinutes())

if __name__ == "__main__":
    fetchBacktradingData()
