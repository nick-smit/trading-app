import datetime

def log(msg: str, write: bool = True):
    print(f"[{datetime.datetime.today().isoformat()}]: {msg}")

    if write:
        file = open("trading.log", "a")
        file.write(f"[{datetime.datetime.today().isoformat()}]: {msg}\n")
        file.close()