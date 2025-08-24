# backtester/event.py
from enum import Enum

class EventType(Enum):
    MARKET = 1    # New market data (a bar)
    SIGNAL = 2    # Strategy generated a signal
    ORDER = 3     # Portfolio wants to place an order
    FILL = 4      # Order has been filled (or partially filled)

class Event:
    """Base class for all events."""
    def __init__(self, event_type: EventType):
        self.type = event_type

class MarketEvent(Event):
    def __init__(self, timestamp, symbol: str, data: dict):
        super().__init__(EventType.MARKET)
        self.timestamp = timestamp
        self.symbol = symbol
        self.data = data # e.g., {'open': 150.0, 'high': 152.0, ... 'volume': 10000}

class SignalEvent(Event):
    def __init__(self, timestamp, symbol: str, direction: str, strength: float = 1.0):
        super().__init__(EventType.SIGNAL)
        self.timestamp = timestamp
        self.symbol = symbol
        self.direction = direction  # 'LONG', 'SHORT', 'EXIT'
        self.strength = strength    # Optional: confidence or sizing factor

class OrderEvent(Event):
    def __init__(self, timestamp, symbol: str, order_type: str, quantity: int, direction: str):
        super().__init__(EventType.ORDER)
        self.timestamp = timestamp
        self.symbol = symbol
        self.order_type = order_type  # 'MKT' (Market), 'LMT' (Limit - for future)
        self.quantity = quantity
        self.direction = direction    # 'BUY' or 'SELL'

class FillEvent(Event):
    def __init__(self, timestamp, symbol: str, quantity: int, direction: str, fill_price: float, commission: float = 0.0):
        super().__init__(EventType.FILL)
        self.timestamp = timestamp
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.fill_price = fill_price
        self.commission = commission
        self.cost = quantity * fill_price + commission if direction == 'BUY' else -quantity * fill_price + commission