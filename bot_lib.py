import config
from helpers import log
from exchange import exchange as _exchange

def getMarkets():
    log("Checking balance")
    balance = _exchange.fetch_balance()

    # Get the market information
    marketsInfo = _exchange.fetch_markets()
    miDict = dict()
    for mi in marketsInfo:
        miDict[mi['symbol']] = mi

    markets = []
    for market in config.markets:
        lot_size = list(filter(lambda x: x['filterType'] == 'LOT_SIZE', miDict[market]['info']['filters']))[0]
        min_qty  = lot_size['minQty']

        # Check if we're already in a position
        currency = market.split('/')[0]
        in_position = balance['free'][currency] > float(min_qty)

        # calculate the maximum decimals of the quantity to buy
        min_qty_decimals = min_qty.replace('0.', '')
        max_decimals = 0
        for i in range(len(min_qty_decimals)):
            max_decimals += 1
            if min_qty_decimals[i] == '1':
                break

        markets.append({'symbol': market, 'in_position': in_position, 'max_decimals': max_decimals})

    return markets

def buy(symbol: str, max_decimals: int):
    balance = _exchange.fetch_balance()
    eurInBalance = balance['free']['EUR']

    price = _exchange.fetch_ticker(symbol)['bid']

    eurToRisk = eurInBalance * config.risk_percentage
    quantity = round(eurToRisk / price, max_decimals)

    order = None
    try:
        order = _exchange.create_market_buy_order(symbol, quantity)
    except Exception as e:
        log(f"Failed to buy {symbol}, got exception: {e}")
        return False

    log(f"Bought {symbol}, order details: \n=====\n{order}\n=====\n")
    return True

def sell(symbol: str):
    balance = _exchange.fetch_balance()
    currency = symbol.split('/')[0]
    quantity = balance['free'][currency]

    order = None
    try:
        order = _exchange.create_market_sell_order(symbol, quantity)
    except Exception as e:
        log(f"Failed to sell {symbol}, got exception: {e}")
        return False
    
    log(f"Sold {symbol}, order details: \n=====\n{order}\n=====\n")
    return True
