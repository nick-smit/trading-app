import config
from fetch_backtrading_lib import *

def fetch60MBacktradingData():
    fetchAllBacktradingData(config.markets, 60)

if __name__ == "__main__":
    fetch60MBacktradingData()
