# PyQuantKit-EventDriven: A Modular Event-Driven Backtester in Python

A from-scratch, event-driven backtesting engine designed to test quantitative trading strategies. This project was built to demonstrate a deep understanding of trading system architecture and to provide a flexible framework for strategy research.

## Project Overview and Goals

The primary goal of this project is to build a robust and modular backtesting system that mimics the operational flow of a live trading environment. Instead of relying heavily on pre-built libraries, this engine is constructed from the ground up to showcase core software design principles like decoupling and event-driven architecture.

**Key Objectives:**
* **Build a Decoupled System:** Each component (Data, Strategy, Portfolio, Execution) operates independently and communicates via a central event queue.
* **Simulate Real-World Trading:** The system accounts for realistic factors like commissions and slippage.
* **Provide Comprehensive Analysis:** Automatically calculates and visualizes key performance metrics such as Sharpe Ratio, Max Drawdown, and the portfolio's equity curve.
* **Ensure Extensibility:** The framework is designed to be easily extendable with new strategies, data sources, and risk management modules.

## Directory Structure Explanation

The project is organized into a modular structure for clarity and scalability:

```
PyQuantKit-EventDriven/
├── backtester/          # Core backtesting engine components
│   ├── __init__.py
│   ├── event.py          # Defines all Event types (Market, Signal, Order, Fill)
│   ├── data.py           # DataHandler for streaming market data
│   ├── strategy.py       # Base class for all trading strategies
│   ├── portfolio.py      # Manages positions, capital, PnL, and generates orders
│   ├── execution.py      # Simulates order execution, including costs
│   ├── performance.py    # Calculates and displays performance metrics
│   └── utils.py          # Utility functions, e.g., for plotting
├── strategies/          # Implementations of specific trading strategies
│   ├── __init__.py
│   ├── dmac.py           # Dual Moving Average Crossover strategy
│   ├── rsi_reversal.py   # RSI Reversal strategy
│   └── bollinger_bands.py# Optional third strategy
├── data/                # Folder for historical market data in CSV format
│   ├── AAPL_1d.csv
│   └── GOOG_1d.csv
├── notebooks/           # Jupyter notebooks for in-depth analysis
│   └── strategy_analysis_AAPL_DMAC.ipynb
├── main.py              # Main script to configure and run the backtest
├── requirements.txt     # List of Python dependencies
├── README.md            
└── .gitignore
```

## Setup Instructions

Follow these steps to set up the project environment and run a backtest.

**1. Prerequisites:**
* Python 3.9 or higher
* Git

**2. Clone the Repository:**
```bash
git clone [https://github.com/YourUsername/PyQuantKit-EventDriven.git](https://github.com/YourUsername/PyQuantKit-EventDriven.git)
cd PyQuantKit-EventDriven
```

**3. Set Up a Virtual Environment (Recommended):**
```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

**4. Install Dependencies:**
The required packages are listed in `requirements.txt`.
```bash
pip install -r requirements.txt
```
The `requirements.txt` file should contain:
```
pandas
numpy
matplotlib
```

**5. Download Market Data:**
* Download historical daily stock data in CSV format (e.g., from Yahoo Finance).
* The CSV file must contain at least these columns: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`.
* Place the data files in the `/data` directory. Name them using the format `SYMBOL_1d.csv` (e.g., `AAPL_1d.csv`).

## How to Run an Example Backtest

The `main.py` script is the entry point for running a backtest. You can configure the symbols, initial capital, and strategy within this file.

**To run the default Dual Moving Average Crossover strategy on AAPL:**
```bash
python main.py
```

**Expected Output:**
You will see log messages in the console tracking the backtest progress, followed by a final performance summary and a plot showing the equity curve and drawdown.

**Console Output Example:**
```
Backtest finished in 1.23 seconds.

--- Performance Summary ---
Initial Capital: $100,000.00
Final Equity:    $152,180.50
Total Return:    52.18%
Sharpe Ratio:    0.85
Max Drawdown:    15.33%
```
A plot window will also appear displaying the results visually.

## Explanation of Core Components

* **Event Queue:** The central message bus of the system. All components communicate by sending and receiving `Event` objects through this queue.
* **Data Handler:** Reads historical data from CSV files and generates `MarketEvent`s for each new bar, simulating a live data feed.
* **Strategy:** The "brains" of the operation. It receives `MarketEvent`s and generates `SignalEvent`s (e.g., LONG, SHORT, EXIT) based on its internal logic.
* **Portfolio:** The risk and position manager. It receives `SignalEvent`s and decides how to size orders, generating `OrderEvent`s. It also receives `FillEvent`s to track its cash, positions, and overall PnL, producing the final equity curve.
* **Execution Handler:** Simulates a brokerage. It receives `OrderEvent`s and converts them into `FillEvent`s, modeling real-world costs like commission and slippage.

## Future Improvements Planned

This project provides a solid foundation. Future enhancements could include:
* [ ] **More Complex Strategies:** Implement statistical arbitrage (pairs trading) or basic machine learning-based strategies.
* [ ] **Advanced Risk Management:** Add dynamic position sizing (e.g., Kelly Criterion, fixed fractional) and stop-loss/take-profit orders.
* [ ] **Support for More Data Sources:** Add handlers for live data from APIs (e.g., Alpaca, Interactive Brokers) or other database formats.
* [ ] **Live Trading Integration:** Develop an `ExecutionHandler` that connects to a real brokerage API to execute live trades.
* [ ] **Enhanced Performance Analytics:** Add more metrics like the Sortino Ratio, Calmar Ratio, and trade-level statistics (win rate, profit factor).
* [ ] **Parameter Optimization:** Build a wrapper around the backtester to systematically test a range of strategy parameters.
* [ ] **Vectorized Backtesting Module:** For comparison, build a simple vectorized backtester to see the speed differences for strategies that don't require path-dependency.