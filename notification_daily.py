import numpy
from notification_lib import sendMail
from helpers import log, isDaylightSavingTime
from datetime import datetime, timedelta
from exchange import exchange as _exchange
import pandas as pd
import config
from pretty_html_table import build_table

float_formatter = lambda x: str(x).replace('.', ',')
euro_formatter = lambda x: '€ ' + float_formatter(round(x, 2))
date_formatter = lambda x: x.strftime('%d-%m-%Y %H:%M')
percent_formatter = lambda x: str(x) + '%'

def getCurrentPrice(symbol, current_prices):
    if current_prices.get(symbol) == None:
        try:
            current_prices[symbol] = _exchange.fetch_ticker(symbol)['bid']
        except Exception as e:
            log("Got exception while trying to fetch ticker for {}: {}".format(symbol, e))
            current_prices[symbol] = 0
    
    return current_prices[symbol]

def getBalanceInEur(current_prices):
    balance = None
    try:
        balance = _exchange.fetch_free_balance()
    except Exception as e:
        log("Got exception while trying to fetch free balance: {}".format(e))
        return 0

    balance_in_eur = 0

    for symbol, value in balance.items():
        if value == 0:
            continue
        
        if symbol == 'EUR':
            balance_in_eur += value
        else:
            balance_in_eur += getCurrentPrice("{}/EUR".format(symbol), current_prices) * value

    
    return balance_in_eur

def dateToString(dt_unix):
    dt_unix /= 1000

    return datetime.fromtimestamp(int(dt_unix)).strftime('%d-%m-%Y %H:%M:%S')

def getTrades():
    trades = pd.DataFrame([], columns=['datetime_close', 'datetime_open', 'amount', 'price_buy', 'price_sell', 'status', 'symbol'])

    for symbol in config.markets:
        positions = _exchange.fetch_orders(symbol)
        positionsDF = pd.DataFrame([], columns=['datetime', 'side', 'amount', 'price'])
        for position in positions:
            positionsDF.loc[len(positionsDF)] = [position['datetime'], position['side'], position['amount'], position['price']]

        positionsDF['datetime'] = pd.to_datetime(positionsDF['datetime'])
        hours_offset = 1
        if isDaylightSavingTime():
            hours_offset = 2
        positionsDF['datetime'] = positionsDF['datetime'].apply(lambda x: x + numpy.timedelta64(hours_offset, 'h'))

        positionsDF['status'] = 'closed'

        if positionsDF.loc[positionsDF.index[-1], 'side'] == 'buy':
            positionsDF.loc[positionsDF.index[-1], 'status'] = 'open'

        i = 0
        while i < len(positionsDF):
            openingTrade = positionsDF.loc[i]
            if openingTrade['side'] == 'buy' and openingTrade['status'] == 'closed':
                i += 1
                closingTrade = positionsDF.loc[i]
                trades.loc[len(trades)] = [closingTrade['datetime'], openingTrade['datetime'], openingTrade['amount'], openingTrade['price'], closingTrade['price'], 'closed', symbol]
            elif openingTrade['status'] == 'open':
                trades.loc[len(trades)] = [numpy.NaN, openingTrade['datetime'], openingTrade['amount'], openingTrade['price'], numpy.NaN, 'open', symbol]
            
            i += 1

    trades['datetime_close'] = pd.to_datetime(trades['datetime_close'])

    trades['profit_per'] = trades['price_sell'] - trades['price_buy']
    trades['total_profit'] = trades['profit_per'] * trades['amount']
    trades['total_investment'] = trades['amount'] * trades['price_buy']
    trades['wl_percent'] = trades['total_profit'] / trades['total_investment'] * 100

    trades['profit_per'] = trades['profit_per'].round(2)
    trades['total_profit'] = trades['total_profit'].round(2)
    trades['total_investment'] = trades['total_investment'].round(2)
    trades['wl_percent'] = trades['wl_percent'].round(2)

    trades = trades.sort_values('datetime_open')

    one_day_ago = datetime.now() - timedelta(1)
    closed_trades = trades.loc[trades['status'] == 'closed'] # only trades that have been closed
    closed_trades = closed_trades.set_index('datetime_close') # set index to datetime_close
    closed_trades = closed_trades.sort_index().loc[one_day_ago.isoformat():] #filter all rows with a closing date before 24 hours ago
    closed_trades = closed_trades.reset_index()

    open_trades = trades.loc[trades['status'] == 'open']

    return (closed_trades, open_trades)

def getTradesMessage(current_prices):
    message = ""

    (closed_trades, open_trades) = getTrades()

    closed_trades['price_buy'] = closed_trades['price_buy'].apply(euro_formatter)
    closed_trades['price_sell'] = closed_trades['price_sell'].apply(euro_formatter)
    closed_trades['total_profit'] = closed_trades['total_profit'].apply(euro_formatter)
    closed_trades['wl_percent'] = closed_trades['wl_percent'].apply(percent_formatter)
    closed_trades['amount'] = closed_trades['amount'].apply(float_formatter)
    closed_trades['datetime_close'] = closed_trades['datetime_close'].apply(date_formatter)

    closed_trades = closed_trades[['datetime_close', 'symbol', 'amount', 'price_buy', 'price_sell', 'wl_percent', 'total_profit']]
    closed_trades.rename(columns={'datetime_close': 'Datum', 'symbol': 'Symbol', 'amount': 'Aantal', 'price_buy': 'Aankoopprijs', 'price_sell': 'Verkoopprijs', 'wl_percent': 'W/L %', 'total_profit': 'W/L €'}, inplace=True)

    open_trades['current_price'] = open_trades['symbol'].apply(lambda symbol: getCurrentPrice(symbol, current_prices))
    open_trades['wl_percent'] = (open_trades['current_price'] / open_trades['price_buy'] * 100 - 100).round(2)
    open_trades['wl_eur'] = ((open_trades['current_price'] - open_trades['price_buy']) * open_trades['amount'])
    
    open_trades['price_buy'] = open_trades['price_buy'].apply(euro_formatter)
    open_trades['current_price'] = open_trades['current_price'].apply(euro_formatter)
    open_trades['wl_eur'] = open_trades['wl_eur'].apply(euro_formatter)
    open_trades['amount'] = open_trades['amount'].apply(float_formatter)
    open_trades['datetime_open'] = open_trades['datetime_open'].apply(date_formatter)
    open_trades['wl_percent'] = open_trades['wl_percent'].apply(percent_formatter)

    open_trades = open_trades[['datetime_open', 'symbol', 'amount', 'price_buy', 'current_price', 'wl_percent', 'wl_eur']]
    open_trades.rename(columns={'datetime_open': 'Datum', 'symbol': 'Symbol', 'amount': 'Aantal', 'price_buy': 'Aankoopprijs', 'current_price': 'Huidige prijs', 'wl_percent': 'W/L %', 'wl_eur': 'W/L €'}, inplace=True)

    message += "<h3>Open trades:</h3>"

    if len(open_trades.index) == 0:
        message += "<p>Momenteel zijn er geen open trades.</p>"
    else:
        message += build_table(open_trades, 'blue_light')

    message += "<h3>Afgeronde trades (afgelopen 24 uur):</h3>"

    if len(closed_trades.index) == 0:
        message += "<p>Er zijn geen afgeronde posities</p>"
    else:
        message+= build_table(closed_trades, 'blue_light')

    return message

def sendDailyNotification(send=True):
    current_prices = dict()

    subject = 'Trading bot log {}'.format(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
    message = ""
    message += "<p><b>De totale waarde van de portefeuille is &euro; %.2f</b></p>" % getBalanceInEur(current_prices)

    message += getTradesMessage(current_prices)

    if send:
        sendMail(subject, message, html=True)
    else:
        log("Subject: {}".format(subject), False)
        log("\n{}".format(message), False)

if __name__ == '__main__':
    sendDailyNotification(False)
