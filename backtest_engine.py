import numpy as np
import pandas as pd

class QuantBacktester:
    """محرك الاختبار التاريخي لتقييم أداء الاستراتيجيات ومحاكاة مونتي كارلو"""
    def __init__(self, initial_capital: float = 10000.0, fee_pct: float = 0.0005):
        self.initial_capital = initial_capital
        self.fee_pct = fee_pct

    def run_backtest(self, df: pd.DataFrame, signals: pd.Series) -> dict:
        capital = self.initial_capital
        equity_curve = [capital]
        trades = []
        current_pos = 0 
        entry_price = 0.0

        for i in range(1, len(df)):
            price = df['close'].iloc[i]
            signal = signals.iloc[i]
            timestamp = df.index[i]

            if current_pos == 1 and signal == 0: 
                pnl = (price - entry_price) / entry_price - (self.fee_pct * 2)
                capital *= (1 + pnl)
                trades.append({'type': 'LONG_CLOSE', 'pnl': pnl, 'capital': capital, 'time': timestamp})
                current_pos = 0

            elif current_pos == -1 and signal == 2: 
                pnl = (entry_price - price) / entry_price - (self.fee_pct * 2)
                capital *= (1 + pnl)
                trades.append({'type': 'SHORT_CLOSE', 'pnl': pnl, 'capital': capital, 'time': timestamp})
                current_pos = 0

            if current_pos == 0:
                if signal == 2:
                    current_pos = 1
                    entry_price = price
                elif signal == 0:
                    current_pos = -1
                    entry_price = price

            equity_curve.append(capital)

        equity_arr = np.array(equity_curve)
        returns = np.diff(equity_arr) / equity_arr[:-1]
        
        total_return = (equity_arr[-1] - self.initial_capital) / self.initial_capital
        sharpe_ratio = (np.mean(returns) / (np.std(returns) + 1e-8)) * np.sqrt(252 * 1440)
        
        peak = np.maximum.accumulate(equity_arr)
        drawdowns = (equity_arr - peak) / peak
        max_drawdown = np.min(drawdowns)

        return {
            "final_capital": capital,
            "total_return_pct": total_return * 100,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown_pct": max_drawdown * 100,
            "total_trades": len(trades),
            "equity_curve": equity_curve
        }

    def monte_carlo_stress_test(self, returns: np.ndarray, num_simulations: int = 1000, forecast_days: int = 30) -> np.ndarray:
        simulation_results = np.zeros((num_simulations, forecast_days))
        for sim in range(num_simulations):
            sim_returns = np.random.choice(returns, size=forecast_days, replace=True)
            simulation_results[sim] = self.initial_capital * np.cumprod(1 + sim_returns)
        return simulation_results
