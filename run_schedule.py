from bot_long_short_sma_crossing import bot_long_short_sma_crossing
from bot_long_short_sma_crossing import bot_long_short_sma_crossing
from notification_daily import sendDailyNotification
from balance_singleton import balance as _balance
import schedule
import time

schedule.every(1).minute.at(':30').do(_balance.RetrieveBalance)
schedule.every(1).minute.at(':05').do(bot_long_short_sma_crossing)
# schedule.every().day.at('12:00').do(sendDailyNotification)
# schedule.every().day.at('08:00').do(sendDailyNotification)
# schedule.every().day.at('18:00').do(sendDailyNotification)
# schedule.every().day.at('22:00').do(sendDailyNotification)
schedule.every().hour.at('00:15').do(sendDailyNotification)

while True:
    schedule.run_pending()
    time.sleep(1)
