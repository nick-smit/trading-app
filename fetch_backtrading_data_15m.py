import config
from fetch_backtrading_lib import *

def fetch15MBacktradingData():
    fetchAllBacktradingData(config.markets, 15)

if __name__ == "__main__":
    fetch15MBacktradingData()
