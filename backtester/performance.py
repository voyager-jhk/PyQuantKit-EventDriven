# backtester/performance.py
import numpy as np
import pandas as pd

def calculate_sharpe_ratio(returns_series, periods_per_year=252, risk_free_rate_annual=0.0):
    """Calculates Sharpe Ratio from a pandas Series of returns."""
    if len(returns_series) < 2: return 0.0
    excess_returns = returns_series - (risk_free_rate_annual / periods_per_year)
    mean_excess_return = np.mean(excess_returns)
    std_dev_excess_return = np.std(excess_returns)
    if std_dev_excess_return == 0: return 0.0 # Avoid division by zero
    return (mean_excess_return / std_dev_excess_return) * np.sqrt(periods_per_year)

def calculate_max_drawdown(equity_curve_series: pd.Series):
    """Calculates Max Drawdown from an equity curve pandas Series."""
    if equity_curve_series.empty: return 0.0, pd.Series(dtype=float)
    cumulative_max = equity_curve_series.cummax()
    drawdown = (equity_curve_series - cumulative_max) / cumulative_max
    max_drawdown_value = drawdown.min() # This will be negative
    return abs(max_drawdown_value), drawdown # Return absolute value for easier interpretation

def display_performance_summary(equity_curve: pd.DataFrame, initial_capital: float):
    if equity_curve.empty or len(equity_curve) < 2:
        print("Not enough data to calculate performance.")
        return

    equity_curve.set_index('timestamp', inplace=True)
    total_return = (equity_curve['total_equity'].iloc[-1] / initial_capital) - 1.0
    daily_returns = equity_curve['total_equity'].pct_change().dropna()

    sharpe = calculate_sharpe_ratio(daily_returns)
    max_dd, dd_series = calculate_max_drawdown(equity_curve['total_equity'])

    print("\n--- Performance Summary ---")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Equity:    ${equity_curve['total_equity'].iloc[-1]:,.2f}")
    print(f"Total Return:    {total_return:.2%}")
    print(f"Sharpe Ratio:    {sharpe:.2f}")
    print(f"Max Drawdown:    {max_dd:.2%}")
    # Add more metrics: Sortino, Calmar, Win Rate, Avg Win/Loss etc. later

    # Plotting (can be in utils.py)
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    equity_curve['total_equity'].plot(ax=ax1, title='Equity Curve', legend=True, ylabel='Portfolio Value')
    ax1.grid(True)

    dd_series.plot(ax=ax2, title='Drawdown Curve', legend=True, color='red', ylabel='Drawdown')
    ax2.fill_between(dd_series.index, dd_series, 0, color='red', alpha=0.3)
    ax2.grid(True)

    plt.tight_layout()
    plt.show()