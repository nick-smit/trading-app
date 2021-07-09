from datetime import datetime
import pytz

#todo rename to helpers.py

def log(msg: str, write: bool = True):
    print(f"[{datetime.today().isoformat()}]: {msg}")

    if write:
        file = open("trading.log", "a")
        file.write(f"[{datetime.today().isoformat()}]: {msg}\n")
        file.close()

#from https://gist.github.com/dpapathanasiou/09bd2885813038d7d3eb
def isDaylightSavingTime ():
    """Determine whether or not Daylight Savings Time (DST)
    is currently in effect"""

    x = datetime(datetime.now().year, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('US/Eastern')) # Jan 1 of this year
    y = datetime.now(pytz.timezone('US/Eastern'))

    # if DST is in effect, their offsets will be different
    return not (y.utcoffset() == x.utcoffset())
