from exchange import exchange as _exchange
from datetime import datetime
from time import sleep
from helpers import log

class Balance():
    def __init__(self):
        self.balanceInEur = None
        self.balanceAge = 0

        self.RetrieveBalance()
    
    def RetrieveBalance(self):
        if datetime.now().timestamp() < self.balanceAge + 59:
            return self.balanceInEur

        log("Fetching balance from API", False)

        try:
            balance = _exchange.fetch_free_balance()
        except Exception as e:
            log("Got exception when fetching balance: {}".format(e))
            if self.balanceInEur != None:
                return self.balanceInEur

            return 0


        balance_in_eur = 0

        for symbol, value in balance.items():
            if value == 0:
                continue
            
            if symbol == 'EUR':
                balance_in_eur += value
            else:
                balance_in_eur += self._GetCurrentPrice("{}/EUR".format(symbol)) * value

        self.balanceAge = datetime.now().timestamp()
        self.balanceInEur = balance_in_eur

        return balance_in_eur

    def _GetCurrentPrice(self, symbol):
        try:
            return _exchange.fetch_ticker(symbol)['bid']
        except Exception as e:
            log("Got exception when fetching ticker {}: {}".format(symbol, e))
            return 0
    

balance = Balance()

if __name__ == '__main__':
    print(balance.RetrieveBalance())
    sleep(15)
    print(balance.RetrieveBalance())