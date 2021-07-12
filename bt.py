from datetime import datetime
from operator import concat, pos
from warnings import catch_warnings
from numpy import NaN, concatenate
import pandas as pd
from os import listdir
from sys import argv
from os.path import isfile, join, basename, splitext
import config

# todo setup argv
tf_in_minutes = 60
import strategy_long_short_sma_crossing as strategy

class Dataprovider():
    def __init__(self, tf_in_minutes):
        dir = f"./backtrading_data_{tf_in_minutes}"
        only_files = [join(dir, f) for f in listdir(dir) if isfile(join(dir, f))]

        self.symbolDict = {}
        for file in only_files:
            symbol = splitext(basename(file))[0]
            self.symbolDict[symbol] = pd.read_csv(file)
        
        earliest_data = None
        latest_data = 0
        for s in self.symbolDict:
            if earliest_data == None or self.symbolDict[s]['timestamp'][0] < earliest_data:
                earliest_data = self.symbolDict[s]['timestamp'][0]
            
            latest = self.symbolDict[s]['timestamp'][len(self.symbolDict[s].index) - 1]
            if latest > latest_data:
                latest_data = latest
            
        tf_in_milliseconds = tf_in_minutes * 60000
        for s in self.symbolDict:
            prepend_data = []
            if self.symbolDict[s]['timestamp'][0] > earliest_data:
                earliest = self.symbolDict[s]['timestamp'][0]
                while earliest > earliest_data:
                    earliest -= tf_in_milliseconds
                    dt = datetime.fromtimestamp(int(earliest / 1000))
                    prepend_data.append([earliest,NaN,NaN,NaN,NaN,NaN,str(dt)])
                prepend_data.reverse()
            
            append_data = []
            latest_idx = len(self.symbolDict[s].index) - 1
            if self.symbolDict[s]['timestamp'][latest_idx] < latest_data:
                latest = self.symbolDict[s]['timestamp'][latest_idx]
                while latest < latest_data:
                    latest += tf_in_milliseconds
                    dt = datetime.fromtimestamp(int(latest / 1000))
                    append_data.append([latest,NaN,NaN,NaN,NaN,NaN,str(dt)])

            if len(prepend_data) == 0 and len(append_data) == 0:
                continue

            data = self.symbolDict[s].to_numpy()
            
            if len(prepend_data) > 0:
                data = concatenate((prepend_data, data))
            
            if len(append_data) > 0:
                data = concatenate((data, append_data))
            
            self.symbolDict[s] = pd.DataFrame(data, columns=self.symbolDict[s].columns)

            # dedupe and fill dataframes
            self.symbolDict[s] = self.symbolDict[s].drop_duplicates(subset='datetime', keep='last')
            r = pd.date_range(start=datetime.fromtimestamp(int(earliest_data / 1000)), end=datetime.fromtimestamp(int(latest_data / 1000)), freq=str(tf_in_minutes) + 'Min')
            self.symbolDict[s]['datetime_idx'] = pd.to_datetime(self.symbolDict[s]['datetime'])
            self.symbolDict[s] = self.symbolDict[s].set_index('datetime_idx').reindex(r, method='pad').reset_index()

            self.len = len(self.symbolDict[s].index)
            

    def retrieveData(self, symbol: str, iteration: int, length: int) -> pd.DataFrame:
        symbol = symbol.replace('/', '')
        return self.symbolDict[symbol].iloc[iteration:iteration+length].reset_index()


dataprovider = Dataprovider(60)

class Position():
    def __init__(self, symbol, quantity, open_price):
        self.symbol = symbol
        self.quantity = quantity
        self.open_price = open_price

class Order():
    def __init__(self, status: str):
        self.status = status

class Wallet():
    def __init__(self, start_euros):
        self.balance = {}
        self.balance['EUR'] = start_euros
    
    def buy(self, symbol, quantity, price) -> Order:
        (currency_to_buy, currency_to_pay_with) = self._splitSymbol(symbol)

        cost = quantity * price

        if not currency_to_pay_with in self.balance:
            self.balance[currency_to_pay_with] = 0

        if cost > self.balance[currency_to_pay_with]:
            return Order('Not enough funds')

        fee = quantity * 0.001

        if not currency_to_buy in self.balance:
            self.balance[currency_to_buy] = 0

        self.balance[currency_to_buy] += quantity - fee
        self.balance[currency_to_pay_with] -= cost

        return Order('Success')

    def sell(self, symbol, quantity, price) -> Order:
        (currency_to_pay_with, currency_to_buy) = self._splitSymbol(symbol)

        if not currency_to_pay_with in self.balance:
            self.balance[currency_to_pay_with] = 0

        if quantity > self.balance[currency_to_pay_with]:
            return Order('Not enough funds')

        returns = quantity * price

        fee = returns * 0.001

        if not currency_to_buy in self.balance:
            self.balance[currency_to_buy] = 0

        self.balance[currency_to_buy] += returns - fee
        self.balance[currency_to_pay_with] -= quantity

        return Order('Success')

    def close(self, symbol, price) -> Order:
        (currency_to_pay_with, currency_to_buy) = self._splitSymbol(symbol)
        quantity = self.balance[currency_to_pay_with]

        return self.sell(symbol, quantity, price)

    def getBalance(self, currency):
        return self.balance[currency]
    

    def _splitSymbol(self, symbol):
        return tuple(symbol.split('/'))




markets = config.markets
risk_percentage = config.risk_percentage

positions = {}
for symbol in markets:
    positions[symbol] = None

wallet = Wallet(500)

trades = []
for i in range(dataprovider.len):
    for s in markets:
        candles = dataprovider.retrieveData(s, i, 30)
        if candles.empty:
            continue

        latest_candle = candles.iloc[-1].copy()

        df = strategy.calculate(candles)
        decision = strategy.make_decision(positions[s], df)
        if decision == 'buy' and positions[s] == None:
            balanceInEur = wallet.getBalance('EUR')
            eurToRisk = balanceInEur * risk_percentage
            price = latest_candle['close']

            quantity = round(eurToRisk / price, 5)
            if wallet.buy(s, quantity, price).status == 'Success':
                positions[s] = Position(s, quantity, price)
        elif decision == 'sell' and positions[s] != None:
            price = latest_candle['close']
            if wallet.close(s, price).status == 'Success':
                profit = round((latest_candle['close'] - positions[s].open_price) * positions[s].quantity, 2)
                print(f"Closed position {s}: {profit}")
                trades.append(profit)
                positions[s] = None
            else:
                print("Failed to close position")

print(f"Wallet at end: {wallet.getBalance('EUR')}")
print(f"Total trades: {len(trades)}")
print(f"Best trade: {max(trades)}")
print(f"Worst trade: {min(trades)}")
print(f"Sum trade: {sum(trades)}")

profitable_trades = [trade for trade in trades if trade > 0]
print(f"Successful trades: {len(profitable_trades) / len(trades)}")