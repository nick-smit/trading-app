from fetch_backtrading_lib import *

def fetch1DBacktradingData():
    symbols = getSymbls()
    fetchAllBacktradingData(symbols, 1440)

if __name__ == "__main__":
    fetch1DBacktradingData()
