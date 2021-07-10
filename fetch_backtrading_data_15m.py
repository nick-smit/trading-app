from fetch_backtrading_lib import *

def fetch15MBacktradingData():
    symbols = getSymbls()
    fetchAllBacktradingData(symbols, 15)

if __name__ == "__main__":
    fetch15MBacktradingData()
