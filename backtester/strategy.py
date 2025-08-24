# backtester/strategy.py
from .event import SignalEvent
from collections import deque # For events_queue

class Strategy:
    """Abstract base class for trading strategies."""
    def __init__(self, events_queue: deque, data_handler, symbol_list: list):
        self.events_queue = events_queue
        self.data_handler = data_handler # To access historical data if needed
        self.symbol_list = symbol_list
        self.bought = {s: False for s in symbol_list} # Simple state tracking

    def calculate_signals(self, market_event) -> None:
        """Processes a MarketEvent and may generate SignalEvents."""
        raise NotImplementedError("Should implement calculate_signals()")
