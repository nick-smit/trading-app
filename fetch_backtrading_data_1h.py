from fetch_backtrading_lib import *

def fetch60MBacktradingData():
    symbols = getSymbls()
    fetchAllBacktradingData(symbols, 60)

if __name__ == "__main__":
    fetch60MBacktradingData()
