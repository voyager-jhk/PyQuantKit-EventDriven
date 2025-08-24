# main.py
from collections import deque
from backtester.data import HistoricCSVDataHandler
from backtester.portfolio import Portfolio
from backtester.execution import SimulatedExecutionHandler
from strategies.dmac import DualMovingAverageCrossover # Import your strategy
from backtester.performance import display_performance_summary
import time

if __name__ == "__main__":
    # Configuration
    csv_dir = './data' # Directory containing your CSV files
    symbol_list = ['AAPL'] # List of symbols to trade
    initial_capital = 100000.0
    start_date = pd.to_datetime('2020-01-01') # Optional: Filter data by date
    end_date = pd.to_datetime('2023-12-31')

    # Initialize components
    events_queue = deque()

    data_handler = HistoricCSVDataHandler(events_queue, csv_dir, symbol_list)
    # Filter data by date if needed
    for sym in symbol_list:
        if sym in data_handler.symbol_data:
            data_handler.symbol_data[sym] = data_handler.symbol_data[sym][
                                             (data_handler.symbol_data[sym].index >= start_date) &
                                             (data_handler.symbol_data[sym].index <= end_date)
                                             ]
            data_handler.symbol_iterators[sym] = data_handler.symbol_data[sym].iterrows()


    strategy = DualMovingAverageCrossover(events_queue, data_handler, symbol_list, short_window=20, long_window=50)
    portfolio = Portfolio(events_queue, data_handler, initial_capital, symbol_list)
    execution_handler = SimulatedExecutionHandler(events_queue)

    start_time = time.time()
    # Main event loop
    while True:
        # 1. Update bars (DataHandler puts MarketEvents onto queue)
        if not data_handler.update_bars(): # update_bars returns False if no more data
            if not events_queue: # And queue is empty
                break # Exit loop if no more data and no events

        # 2. Process events from the queue
        while True:
            try:
                event = events_queue.popleft()
            except IndexError:
                # Queue is empty for now
                break
            else:
                if event.type == 'MARKET':
                    # print(f"Time: {event.timestamp}, Symbol: {event.symbol}, Price: {event.data['close']}") # For debugging
                    strategy.calculate_signals(event)
                    portfolio.update_timeindex(event) # Update portfolio value based on new market data

                elif event.type == 'SIGNAL':
                    # print(f"Time: {event.timestamp}, Signal: {event.direction} for {event.symbol}") # For debugging
                    portfolio.update_signal(event)

                elif event.type == 'ORDER':
                    # print(f"Time: {event.timestamp}, Order: {event.direction} {event.quantity} of {event.symbol}") # For debugging
                    execution_handler.execute_order(event, data_handler) # Pass data_handler for fill price

                elif event.type == 'FILL':
                    # print(f"Time: {event.timestamp}, Fill: {event.direction} {event.quantity} of {event.symbol} at ${event.fill_price:.2f}") # Debug
                    portfolio.update_fill(event)

    end_time = time.time()
    print(f"\nBacktest finished in {end_time - start_time:.2f} seconds.")

    # Post-backtest analysis
    equity_curve_df = portfolio.get_equity_curve()
    display_performance_summary(equity_curve_df, initial_capital)