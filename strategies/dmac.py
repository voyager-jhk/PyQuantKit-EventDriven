# strategies/dmac.py (Dual Moving Average Crossover)
import pandas as pd
from backtester.strategy import Strategy
from backtester.event import SignalEvent


class DualMovingAverageCrossover(Strategy):
    def __init__(
        self,
        events_queue,
        data_handler,
        symbol_list: list,
        short_window=50,
        long_window=200,
    ):
        super().__init__(events_queue, data_handler, symbol_list)
        self.short_window = short_window
        self.long_window = long_window
        # Store recent close prices to calculate MAs
        self.prices = {s: pd.Series(dtype=float) for s in symbol_list}
        self.signals = {s: "" for s in symbol_list}  # To avoid duplicate signals

    def calculate_signals(self, market_event):
        if market_event.type == "MARKET":
            symbol = market_event.symbol
            new_price = market_event.data["close"]

            # Append new price and keep only necessary length
            self.prices[symbol] = pd.concat(
                [
                    self.prices[symbol],
                    pd.Series([new_price], index=[market_event.timestamp]),
                ]
            )
            self.prices[symbol] = self.prices[symbol][
                -self.long_window :
            ]  # Keep only relevant window

            if len(self.prices[symbol]) >= self.long_window:
                short_ma = (
                    self.prices[symbol]
                    .rolling(window=self.short_window)
                    .mean()
                    .iloc[-1]
                )
                long_ma = (
                    self.prices[symbol].rolling(window=self.long_window).mean().iloc[-1]
                )

                current_signal = ""
                if (
                    short_ma > long_ma
                    and self.prices[symbol]
                    .iloc[-2]
                    .rolling(window=self.short_window)
                    .mean()
                    <= self.prices[symbol]
                    .iloc[-2]
                    .rolling(window=self.long_window)
                    .mean()
                ):
                    current_signal = (
                        "LONG"  # Buy signal (short MA crosses above long MA)
                    )
                elif (
                    short_ma < long_ma
                    and self.prices[symbol]
                    .iloc[-2]
                    .rolling(window=self.short_window)
                    .mean()
                    >= self.prices[symbol]
                    .iloc[-2]
                    .rolling(window=self.long_window)
                    .mean()
                ):
                    current_signal = "EXIT"  # Sell signal (short MA crosses below long MA or exit long)

                if (
                    current_signal and self.signals[symbol] != current_signal
                ):  # New signal
                    sig_event = SignalEvent(
                        timestamp=market_event.timestamp,
                        symbol=symbol,
                        direction=current_signal,
                    )
                    self.events_queue.append(sig_event)
                    self.signals[symbol] = current_signal
                elif (
                    not current_signal and self.signals[symbol] == "LONG"
                ):  # Condition no longer met, but no explicit exit signal from MA cross-down
                    pass  # Hold, or implement specific exit logic if needed
