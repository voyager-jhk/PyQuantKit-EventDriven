# backtester/execution.py
from .event import FillEvent, OrderEvent
from collections import deque

class ExecutionHandler:
    """Abstract base class for execution handlers."""
    def __init__(self, events_queue: deque):
        self.events_queue = events_queue

    def execute_order(self, order_event: OrderEvent, data_handler) -> None: # Added data_handler
        """Simulates order execution and generates a FillEvent."""
        raise NotImplementedError("Should implement execute_order()")

class SimulatedExecutionHandler(ExecutionHandler):
    def __init__(self, events_queue: deque, commission_per_share=0.001, slippage_pct=0.0005): # Added slippage
        super().__init__(events_queue)
        self.commission_per_share = commission_per_share
        self.slippage_pct = slippage_pct # Percentage slippage

    def execute_order(self, order_event: OrderEvent, data_handler): # Added data_handler
        symbol = order_event.symbol
        quantity = order_event.quantity
        direction = order_event.direction # 'BUY' or 'SELL'

        # Simulate fill: use next bar's open price for simplicity
        # A more realistic simulation would use current bar's close, or VWAP, or have a proper matching engine
        latest_bar = data_handler.get_latest_bar(symbol)
        if latest_bar is None or latest_bar.get('open') is None:
             # This happens if an order is generated but there's no subsequent market data for fill price.
             # Could be end of data, or data issue. Skip fill or use last known close.
            print(f"Warning: No market data to fill order for {symbol} at {order_event.timestamp}. Order skipped.")
            return

        fill_price = latest_bar['open'] # Fill at next available open

        # Simulate slippage
        if direction == 'BUY':
            fill_price *= (1 + self.slippage_pct)
        else: # SELL
            fill_price *= (1 - self.slippage_pct)

        commission = self.commission_per_share * quantity
        fill_event = FillEvent(
            timestamp=order_event.timestamp, # Or use timestamp from latest_bar if fill is on next tick
            symbol=symbol,
            quantity=quantity,
            direction=direction,
            fill_price=fill_price,
            commission=commission
        )
        self.events_queue.append(fill_event)