"""
Backtesting Engine - Test trading strategies on historical data
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.utils.logger import get_logger


class BacktestEngine:
    """Engine for backtesting trading strategies"""

    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.logger = get_logger("BacktestEngine")

    async def run_backtest(self, strategy, market_data_api,
                          symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Run backtest for a strategy

        Args:
            strategy: Trading strategy to test
            market_data_api: Market data API
            symbol: Trading symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dictionary with backtest results
        """
        self.logger.info(f"Starting backtest for {symbol}")
        self.logger.info(f"Period: {start_date} to {end_date}")
        self.logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")

        # Get historical data
        df = await market_data_api.get_ohlcv(symbol, timeframe='1h', limit=1000)

        # Initialize tracking variables
        cash = self.initial_capital
        position = None
        trades = []
        equity_curve = []

        # Simulate trading
        for i in range(100, len(df)):  # Start after enough data for indicators
            current_data = df.iloc[:i+1]
            current_price = current_data['close'].iloc[-1]
            timestamp = current_data.index[-1]

            # Get signal from strategy
            market_data = {
                'df': current_data,
                'symbol': symbol,
                'timeframe': '1h'
            }

            signal = await strategy.generate_signal(market_data)

            # Execute trades based on signal
            if signal and signal.signal_type in ['buy', 'strong_buy'] and position is None:
                # Buy
                position_size = cash * 0.95  # Use 95% of capital
                quantity = position_size / current_price
                position = {
                    'entry_price': current_price,
                    'quantity': quantity,
                    'entry_time': timestamp
                }
                cash -= position_size

                self.logger.debug(f"BUY: {quantity:.6f} @ ${current_price:.2f}")

            elif signal and signal.signal_type in ['sell', 'strong_sell'] and position is not None:
                # Sell
                exit_value = position['quantity'] * current_price
                pnl = exit_value - (position['quantity'] * position['entry_price'])
                pnl_pct = (pnl / (position['quantity'] * position['entry_price'])) * 100

                trades.append({
                    'entry_time': position['entry_time'],
                    'exit_time': timestamp,
                    'entry_price': position['entry_price'],
                    'exit_price': current_price,
                    'quantity': position['quantity'],
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })

                cash += exit_value
                position = None

                self.logger.debug(f"SELL: PnL ${pnl:.2f} ({pnl_pct:.2f}%)")

            # Track equity
            total_equity = cash
            if position:
                total_equity += position['quantity'] * current_price

            equity_curve.append({
                'timestamp': timestamp,
                'equity': total_equity
            })

        # Calculate final results
        final_equity = cash
        if position:
            final_equity += position['quantity'] * df['close'].iloc[-1]

        results = self._calculate_metrics(trades, equity_curve, final_equity)

        self.logger.info("Backtest completed")
        self.logger.info(f"Final Equity: ${results['final_equity']:,.2f}")
        self.logger.info(f"Total Return: {results['total_return']:.2f}%")
        self.logger.info(f"Win Rate: {results['win_rate']:.1f}%")
        self.logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")

        return results

    def _calculate_metrics(self, trades: List[Dict], equity_curve: List[Dict],
                          final_equity: float) -> Dict[str, Any]:
        """Calculate backtest performance metrics"""
        # Basic metrics
        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        total_trades = len(trades)

        if total_trades == 0:
            return {
                'initial_capital': self.initial_capital,
                'final_equity': final_equity,
                'total_return': total_return,
                'total_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'trades': []
            }

        # Win/Loss metrics
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]

        win_rate = (len(winning_trades) / total_trades) * 100
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t['pnl']) for t in losing_trades]) if losing_trades else 0

        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = sum(abs(t['pnl']) for t in losing_trades)
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Sharpe Ratio
        returns = [t['pnl_pct'] for t in trades]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if len(returns) > 1 else 0

        # Max Drawdown
        equity_values = [e['equity'] for e in equity_curve]
        max_drawdown = self._calculate_max_drawdown(equity_values)

        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'trades': trades,
            'equity_curve': equity_curve
        }

    def _calculate_max_drawdown(self, equity_values: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not equity_values:
            return 0

        peak = equity_values[0]
        max_dd = 0

        for value in equity_values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd

        return max_dd * 100
