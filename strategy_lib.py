from os import system
from typing import Optional
import pandas as pd
from enum import Enum

class Position():
    def __init__(self, symbol: str, status: bool = False, quantity: float = None, open_price: float = None, stoploss: float = None, take_profit: float = None):
        self.symbol = symbol
        self.status = status
        self.quantity = quantity
        self.open_price = open_price
        self.stoploss = stoploss
        self.take_profit = take_profit
    
    def InPosition(self) -> bool:
        return self.status

    def GetQuantity(self) -> Optional[float]:
        if self.InPosition():
            return self.quantity

        return None

    def GetOpenPrice(self) -> Optional[float]:
        if self.InPosition():
            return self.open_price
        
        return None

    def GetStoploss(self) -> Optional[float]:
        if self.InPosition():
            return self.stoploss
        
        return None

    def GetTakeProfit(self) -> Optional[float]:
        if self.InPosition():
            return self.take_profit
        
        return None

class Side(Enum):
    SELL = 0
    BUY = 1

    def __repr__(self):
        if self.value == Side.SELL:
            return 'SELL'
        if self.value == Side.BUY:
            return 'BUY'

class Receipt:
    def __init__(self, side: Side, stoploss: float = None, take_profit: float = None):
        self.side = side
        self.stoploss = stoploss
        self.take_profit = take_profit

    def __repr__(self):
        stoploss = ""
        if self.stoploss != None:
            stoploss    = f"\nStoploss:    {self.stoploss}"

        take_profit = ""
        if self.take_profit != None:
            take_profit = f"\nTake profit: {self.take_profit}"

        return f"{str(self.side)}{stoploss}{take_profit}"

class CandleTimeframe(Enum):
    ONE_MIN = '1m'
    THREE_MIN = '3m'
    FIVE_MIN = '5m'
    FIFTEEN_MIN = '15m'
    THIRTY_MIN = '30m'
    ONE_HOUR = '1h'
    TWO_HOUR = '2h'
    FOUR_HOUR = '4h'
    SIX_HOUR = '6h'
    EIGHT_HOUR = '8h'
    TWELVE_HOUR = '12h'
    ONE_DAY = '1d'
    THREE_DAY = '3d'
    ONE_WEEK = '1w'

    def GetInMinutes(self) -> int:
        if self == CandleTimeframe.ONE_MIN:
            return 1
        if self == CandleTimeframe.THREE_MIN:
            return 3
        if self == CandleTimeframe.FIVE_MIN:
            return 5
        if self == CandleTimeframe.FIFTEEN_MIN:
            return 15
        if self == CandleTimeframe.THIRTY_MIN:
            return 30
        if self == CandleTimeframe.ONE_HOUR:
            return 60
        if self == CandleTimeframe.TWO_HOUR:
            return 120
        if self == CandleTimeframe.FOUR_HOUR:
            return 240
        if self == CandleTimeframe.SIX_HOUR:
            return 360
        if self == CandleTimeframe.EIGHT_HOUR:
            return 480
        if self == CandleTimeframe.TWELVE_HOUR:
            return 720
        if self == CandleTimeframe.ONE_DAY:
            return 1440
        if self == CandleTimeframe.THREE_DAY:
            return 4320
        if self == CandleTimeframe.ONE_WEEK:
            return 10080

class BaseStrat():
    def GetCandleTimeframe(self) -> CandleTimeframe:
        return CandleTimeframe.ONE_HOUR

    def GetMinCandles(self) -> int:
        return 20

    def OnCandleClose(self, candles:pd.DataFrame, position: Position) -> Optional[Receipt]:
        return None

    def OnTick(self, candle: dict, position: Position) -> Optional[Receipt]:
        return None
