from enum import Enum
from pydantic import BaseModel
import pandas as pd

#Definicion de los distintos tipos de eventos
class EventType(str, Enum):
    DATA = "DATA"
    SIGNAL = "SIGNAL"
    SIZING = "SIZING"
    ORDER = "ORDER"

class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"

class BaseEvent(BaseModel):
    event_type: EventType

    #Clase dentro de BaseEvent
    class Config:
        arbitrary_types_allowed = True

class DataEvent(BaseEvent):
    event_type: EventType = EventType.DATA
    symbol: str
    data: pd.Series

class SignalEvent(BaseEvent):
    event_type: EventType = EventType.SIGNAL
    symbol: str
    signal: SignalType
    target_order: OrderType
    target_price: float
    magic_number: int
    sl: float
    tp: float

class SizingEvent(BaseEvent):
    event_type: EventType = EventType.SIZING
    symbol: str
    signal: SignalType
    target_order: OrderType
    target_price: float
    magic_number: int
    sl: float
    tp: float
    volume: float

class OrderEvent(BaseEvent):
    event_type: EventType = EventType.ORDER
    symbol: str
    signal: SignalType
    target_order: OrderType
    target_price: float
    magic_number: int
    sl: float
    tp: float
    volume: float   