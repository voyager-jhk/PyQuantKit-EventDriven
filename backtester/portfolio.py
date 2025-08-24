# backtester/portfolio.py
import pandas as pd
from .event import OrderEvent, FillEvent
from collections import deque

class Portfolio:
    def __init__(self, events_queue: deque, data_handler, initial_capital=100000.0, symbol_list: list = None):
        self.events_queue = events_queue
        self.data_handler = data_handler
        self.symbol_list = symbol_list if symbol_list is not None else []
        self.initial_capital = initial_capital
        self.current_cash = initial_capital

        self.current_positions = {s: 0 for s in self.symbol_list} # Quantity of shares
        self.current_holdings_value = {s: 0.0 for s in self.symbol_list} # Market value of shares
        self.total_market_value = 0.0 # Sum of all holdings_value + cash

        # For PnL tracking and equity curve
        self.all_positions = [] # List of position dicts at each timestamp
        self.all_holdings = []  # List of holdings dicts at each timestamp
        self.equity_curve = pd.DataFrame(columns=['timestamp', 'total_equity', 'cash', 'holdings_value'])


    def update_timeindex(self, market_event):
        """
        Updates the portfolio's holdings value based on the latest market data.
        This is called at each 'heartbeat' of the backtest.
        """
        timestamp = market_event.timestamp # Assuming all symbols get a market event for a given timestamp in a batch
                                        # Or, if processing symbol by symbol, this needs careful handling

        # Update holdings value for each symbol
        current_total_holdings_value = 0.0
        for symbol in self.symbol_list:
            if self.current_positions[symbol] != 0:
                latest_bar = self.data_handler.get_latest_bar(symbol)
                if latest_bar:
                    self.current_holdings_value[symbol] = self.current_positions[symbol] * latest_bar['close']
                # else: market data not available, use last known value or handle
            else:
                self.current_holdings_value[symbol] = 0.0
            current_total_holdings_value += self.current_holdings_value[symbol]

        self.total_market_value = self.current_cash + current_total_holdings_value

        # Record equity
        new_equity_row = pd.DataFrame([{
            'timestamp': timestamp,
            'total_equity': self.total_market_value,
            'cash': self.current_cash,
            'holdings_value': current_total_holdings_value
        }])
        self.equity_curve = pd.concat([self.equity_curve, new_equity_row], ignore_index=True)

        # Store snapshots (optional, can make equity_curve large)
        # self.all_positions.append(self.current_positions.copy())
        # self.all_holdings.append(self.current_holdings_value.copy())


    def update_signal(self, signal_event: SignalEvent):
        """Acts on a SignalEvent to generate OrderEvents."""
        symbol = signal_event.symbol
        direction = signal_event.direction # 'LONG', 'SHORT', 'EXIT'
        timestamp = signal_event.timestamp

        # Basic order sizing: 100 shares for now, or fixed monetary amount
        # TODO: Implement more sophisticated position sizing (e.g., % of equity)
        target_quantity = 100 # Example fixed quantity
        order_type = 'MKT'

        current_quantity = self.current_positions[symbol]

        if direction == 'LONG' and current_quantity == 0:
            order = OrderEvent(timestamp, symbol, order_type, target_quantity, 'BUY')
            self.events_queue.append(order)
        elif direction == 'EXIT' and current_quantity > 0: # Exit long position
            order = OrderEvent(timestamp, symbol, order_type, current_quantity, 'SELL')
            self.events_queue.append(order)
        # Add SHORT logic if desired

    def update_fill(self, fill_event: FillEvent):
        """Updates portfolio state based on a FillEvent."""
        symbol = fill_event.symbol
        fill_cost = fill_event.cost # Negative for sell, positive for buy (already includes commission)

        self.current_cash -= fill_cost # fill_cost includes commission and sign

        if fill_event.direction == 'BUY':
            self.current_positions[symbol] += fill_event.quantity
        elif fill_event.direction == 'SELL':
            self.current_positions[symbol] -= fill_event.quantity

        # Update holdings value immediately after fill (or wait for next market tick)
        latest_bar = self.data_handler.get_latest_bar(symbol)
        if latest_bar:
            self.current_holdings_value[symbol] = self.current_positions[symbol] * latest_bar['close']
        else: # If no current bar (e.g. EOD fill), use fill_price as an estimate
             self.current_holdings_value[symbol] = self.current_positions[symbol] * fill_event.fill_price


    def get_equity_curve(self):
        if not self.equity_curve.empty:
            self.equity_curve.set_index('timestamp', inplace=True)
        return self.equity_curve