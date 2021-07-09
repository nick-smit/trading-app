from bot_long_short_sma_crossing import bot_long_short_sma_crossing
from bot_long_short_sma_crossing import bot_long_short_sma_crossing
import schedule
import time

schedule.every(1).minute.do(bot_long_short_sma_crossing)

schedule.run_all()
while True:
    schedule.run_pending()
    time.sleep(1)
