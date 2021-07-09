import config
from fetch_backtrading_lib import *

def fetch1DBacktradingData():
    fetchAllBacktradingData(config.markets, 1440)

if __name__ == "__main__":
    fetch1DBacktradingData()
