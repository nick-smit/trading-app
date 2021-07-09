import os
from datetime import datetime
import exchange
from log import log

def calculateNextFromDate(from_date, tf_in_minutes):
    return int(from_date + (60000 * tf_in_minutes))

def fetchSymbolData(symbol, tf_in_minutes, from_date):
    from_date = int(datetime.strptime(from_date, '%Y-%m-%d').timestamp() * 1000)
    now = int(datetime.now().timestamp() * 1000)

    is_first = True

    dirname = f"./backtrading_data_{tf_in_minutes}"
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    filename = f"{dirname}/{symbol.replace('/','')}.csv"
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            f.readline()
            for last_line in f:
                pass

            ts = last_line.split(',')[0]
            from_date = calculateNextFromDate(int(ts), tf_in_minutes)
            is_first = False

    while(from_date < now):
        log("Fetching data for {} from {}".format(symbol, from_date), False)

        data = exchange.exchange.fetch_ohlcv(symbol, '15m', params={'startTime': from_date})

        df = exchange.candlesToDataFrame(data)
        if len(df.index) == 0:
            break

        header = False
        if (is_first):
            header = df.columns

        df.to_csv(filename,mode='a',header=header, index=False)
        is_first = False

        last = df.iloc[-1]['timestamp']
        from_date = calculateNextFromDate(last, tf_in_minutes)

def fetchAllBacktradingData(markets, tf_in_minutes, from_date='2020-01-01'):
    log("Fetching backtrading data", False)
    for symbol in markets:
        fetchSymbolData(symbol, tf_in_minutes, from_date)
