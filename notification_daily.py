from notification_lib import sendMail
from helpers import log, isDaylightSavingTime
from datetime import datetime
from exchange import exchange as _exchange
import config

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


def getTradesMessage(current_prices):
    message = ""

    now = int(datetime.now().timestamp());
    one_day_ago = now - (60 * 60 * 24)
    if isDaylightSavingTime():
        now -= 60 * 60 * 2
        one_day_ago -= 60 * 60 * 2
    else:
        now -= 60 * 60
        one_day_ago -= 60 * 60

    completed_trades = []
    incomplete_trades = []
    for symbol in config.markets:
        trades = None
        try:
            trades = _exchange.fetch_orders(symbol, since= one_day_ago * 1000)
        except Exception as e:
            log("Got exception while trying to fetch orders for {}: {}".format(symbol, e))
            continue

        print(trades)
        i = 0
        while i < len(trades):
            if trades[i]['side'] == 'sell':
                # we only want trading pairs, or buying trades
                i += 1
                continue

            if i+1 < len(trades):
                completed_trades.append([trades[i], trades[i+1]])
                i += 1
            else:
                incomplete_trades.append(trades[i])
            
            i += 1

    message += "<h3>Open trades:</h3>"
    message += "<table>"
    message += "<tr><th>Symbol</th><th>Aantal</th><th>Aankoop Datum</th><th>Aankoop prijs</th><th>Huidige prijs</th><th>W/L%</th></tr>"

    for trade in incomplete_trades:
        price = getCurrentPrice(trade['symbol'], current_prices)
        wlpercent = round((price / trade['price'] * 100) - 100, 2)
        color = 'green'
        if wlpercent < 0:
            color = 'red'

        dt = dateToString(trade['timestamp'])

        message += "<tr>"
        message += "<td>{}</td>".format(trade['symbol'])
        message += "<td>{}</td>".format(trade['amount'])
        message += "<td>{}</td>".format(dt)
        message += "<td>{}</td>".format(round(trade['price'], 5))
        message += "<td>{}</td>".format(round(price, 5))
        message += f"<td style=\"color: {color};\">{wlpercent}%</td>"
        message += "</tr>"

    message += "</table>"


    message += "<h3>Completed trades:</h3>"
    message += "<table>"
    message += "<tr><th>Symbol</th><th>Aantal</th><th>Aankoop datum</th><th>Aankoop prijs</th><th>Verkoop datum</th><th>Verkoop prijs</th><th>W/L%</th></tr>"

    for trade in completed_trades:
        open_trade = trade[0]
        close_trade = trade[1]

        wlpercent = round((close_trade['price'] / open_trade['price'] * 100) - 100, 2)
        color = 'green'
        if wlpercent < 0:
            color = 'red'

        buy_dt = dateToString(open_trade['timestamp'])
        sell_dt = dateToString(close_trade['timestamp'])

        message += "<tr>"
        message += "<td>{}</td>".format(open_trade['symbol'])
        message += "<td>{}</td>".format(open_trade['amount'])
        message += "<td>{}</td>".format(buy_dt)
        message += "<td>{}</td>".format(round(open_trade['price'], 5))
        message += "<td>{}</td>".format(sell_dt)
        message += "<td>{}</td>".format(round(close_trade['price'], 5))
        message += f"<td style=\"color: {color};\">{wlpercent}%</td>"
        message += "</tr>"

    message += "</table>"
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
    sendDailyNotification(True)