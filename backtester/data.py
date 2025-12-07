# backtester/data.py
import pandas as pd
from collections import deque
from .event import MarketEvent


class DataHandler:
    """Abstract base class for data handlers."""

    def __init__(self, events_queue: deque, symbol_list: list):
        self.events_queue = events_queue
        self.symbol_list = symbol_list
        self.latest_symbol_data = {
            s: {} for s in symbol_list
        }  # Stores latest bar for each symbol

    def get_latest_bar(self, symbol: str) -> dict:
        """Returns the last updated bar for a symbol."""
        return self.latest_symbol_data.get(symbol, None)

    def update_bars(self) -> bool:
        """
        Pushes the latest bar data for all symbols onto the event queue.
        Returns True if there is more data, False otherwise.
        """
        raise NotImplementedError("Should implement update_bars()")


class HistoricCSVDataHandler(DataHandler):
    def __init__(self, events_queue: deque, csv_dir: str, symbol_list: list):
        super().__init__(events_queue, symbol_list)
        self.csv_dir = csv_dir
        self.symbol_data = {}  # Stores full DataFrame for each symbol
        self.symbol_iterators = {}  # Iterators for each symbol's DataFrame

        self._load_csv_data()

    def _load_csv_data(self):
        for symbol in self.symbol_list:
            file_path = (
                f"{self.csv_dir}/{symbol}_1d.csv"  # Assuming 'SYMBOL_1d.csv' format
            )
            try:
                # Assuming CSV has columns: Date,Open,High,Low,Close,Adj Close,Volume
                # Make sure 'Date' is parsed as datetime
                df = pd.read_csv(file_path, index_col="Date", parse_dates=True)
                df.sort_index(inplace=True)  # Ensure chronological order
                self.symbol_data[symbol] = df
                self.symbol_iterators[symbol] = self.symbol_data[symbol].iterrows()
            except FileNotFoundError:
                print(f"Warning: Data file for {symbol} not found at {file_path}")
                self.symbol_list.remove(symbol)  # Or handle more gracefully

    def update_bars(self) -> bool:
        """
        Pushes the next bar for each symbol onto the events queue.
        Returns True if any iterator still has data.
        """
        more_data = False
        for symbol in self.symbol_list:
            try:
                timestamp, row = next(self.symbol_iterators[symbol])
                bar_data = {
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"],
                    "adj_close": row.get("Adj Close", row["Close"]),
                }
                self.latest_symbol_data[symbol] = bar_data
                market_event = MarketEvent(
                    timestamp=timestamp, symbol=symbol, data=bar_data
                )
                self.events_queue.append(market_event)  # Use append for deque
                more_data = True
            except StopIteration:
                # No more data for this symbol
                pass
            except KeyError as e:
                print(
                    f"Error accessing data for {symbol} at {timestamp}: {e}. Row: {row}"
                )
                # Potentially remove symbol or handle
        return more_data
