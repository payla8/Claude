"""
Portfolio Manager - Tracks and manages portfolio positions and performance
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from src.utils.logger import get_logger


@dataclass
class Position:
    """Represents a trading position"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    entry_time: datetime
    side: str = 'long'  # 'long' or 'short'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    @property
    def value(self) -> float:
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.quantity * self.entry_price

    @property
    def pnl(self) -> float:
        if self.side == 'long':
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity

    @property
    def pnl_percentage(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return (self.pnl / self.cost_basis) * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'value': self.value,
            'cost_basis': self.cost_basis,
            'pnl': self.pnl,
            'pnl_percentage': self.pnl_percentage,
            'entry_time': self.entry_time.isoformat(),
            'side': self.side,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        }


class PortfolioManager:
    """Manages portfolio positions and tracks performance"""

    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Dict[str, Any]] = []
        self.logger = get_logger("PortfolioManager")

        self.logger.info(f"Portfolio initialized with ${initial_capital:,.2f}")

    def add_position(self, symbol: str, quantity: float, price: float,
                    side: str = 'long', stop_loss: Optional[float] = None,
                    take_profit: Optional[float] = None) -> Position:
        """Add a new position to the portfolio"""
        cost = quantity * price

        if cost > self.cash:
            self.logger.warning(
                f"Insufficient funds to open position: "
                f"Required ${cost:.2f}, Available ${self.cash:.2f}"
            )
            # Allow position but log warning (in real scenario might reject)

        position = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=price,
            current_price=price,
            entry_time=datetime.now(),
            side=side,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        # If position already exists, average in
        if symbol in self.positions:
            existing = self.positions[symbol]
            total_quantity = existing.quantity + quantity
            avg_price = (
                (existing.entry_price * existing.quantity + price * quantity) /
                total_quantity
            )
            existing.quantity = total_quantity
            existing.entry_price = avg_price
            position = existing
            self.logger.info(
                f"Averaged into {symbol} position - "
                f"New quantity: {total_quantity:.6f}, Avg price: ${avg_price:.2f}"
            )
        else:
            self.positions[symbol] = position
            self.logger.info(
                f"Opened {side} position: {quantity:.6f} {symbol} @ ${price:.2f} "
                f"(Total: ${cost:.2f})"
            )

        self.cash -= cost

        return position

    def close_position(self, symbol: str, price: float,
                      partial_quantity: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Close a position (fully or partially)"""
        if symbol not in self.positions:
            self.logger.warning(f"No position found for {symbol}")
            return None

        position = self.positions[symbol]
        close_quantity = partial_quantity if partial_quantity else position.quantity

        if close_quantity > position.quantity:
            self.logger.warning(
                f"Cannot close {close_quantity} - only {position.quantity} available"
            )
            return None

        # Update current price and calculate PnL
        position.current_price = price
        pnl = ((price - position.entry_price) * close_quantity
               if position.side == 'long'
               else (position.entry_price - price) * close_quantity)

        pnl_pct = (pnl / (position.entry_price * close_quantity)) * 100

        # Add cash from closing position
        self.cash += close_quantity * price

        # Create closed position record
        closed_record = {
            'symbol': symbol,
            'side': position.side,
            'entry_price': position.entry_price,
            'exit_price': price,
            'quantity': close_quantity,
            'pnl': pnl,
            'pnl_percentage': pnl_pct,
            'entry_time': position.entry_time,
            'exit_time': datetime.now(),
            'holding_period': (datetime.now() - position.entry_time).total_seconds() / 3600  # hours
        }

        self.closed_positions.append(closed_record)

        # Update or remove position
        if close_quantity < position.quantity:
            position.quantity -= close_quantity
            self.logger.info(
                f"Partially closed {symbol} position: {close_quantity:.6f} @ ${price:.2f} "
                f"(PnL: ${pnl:.2f} / {pnl_pct:.2f}%)"
            )
        else:
            del self.positions[symbol]
            self.logger.info(
                f"Closed {symbol} position: {close_quantity:.6f} @ ${price:.2f} "
                f"(PnL: ${pnl:.2f} / {pnl_pct:.2f}%)"
            )

        return closed_record

    def update_prices(self, prices: Dict[str, float]):
        """Update current prices for all positions"""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = price

    def get_portfolio_value(self) -> float:
        """Get total portfolio value"""
        positions_value = sum(pos.value for pos in self.positions.values())
        return self.cash + positions_value

    def get_total_pnl(self) -> float:
        """Get total P&L (realized + unrealized)"""
        # Unrealized P&L from open positions
        unrealized_pnl = sum(pos.pnl for pos in self.positions.values())

        # Realized P&L from closed positions
        realized_pnl = sum(trade['pnl'] for trade in self.closed_positions)

        return realized_pnl + unrealized_pnl

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        total_value = self.get_portfolio_value()
        total_pnl = self.get_total_pnl()
        total_return_pct = ((total_value - self.initial_capital) / self.initial_capital) * 100

        # Calculate win rate from closed positions
        if self.closed_positions:
            winning_trades = len([t for t in self.closed_positions if t['pnl'] > 0])
            total_trades = len(self.closed_positions)
            win_rate = (winning_trades / total_trades) * 100

            avg_win = np.mean([t['pnl'] for t in self.closed_positions if t['pnl'] > 0]) if winning_trades > 0 else 0
            avg_loss = np.mean([t['pnl'] for t in self.closed_positions if t['pnl'] < 0]) if (total_trades - winning_trades) > 0 else 0

            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        else:
            win_rate = 0
            total_trades = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0

        return {
            'initial_capital': self.initial_capital,
            'current_value': total_value,
            'cash': self.cash,
            'positions_value': sum(pos.value for pos in self.positions.values()),
            'total_pnl': total_pnl,
            'total_return_pct': total_return_pct,
            'open_positions': len(self.positions),
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }

    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        return [pos.to_dict() for pos in self.positions.values()]

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get specific position"""
        return self.positions.get(symbol)

    def has_position(self, symbol: str) -> bool:
        """Check if position exists"""
        return symbol in self.positions

    def get_exposure(self) -> float:
        """Get total portfolio exposure as percentage"""
        positions_value = sum(pos.value for pos in self.positions.values())
        total_value = self.get_portfolio_value()
        return (positions_value / total_value) * 100 if total_value > 0 else 0


# Import numpy for metrics calculation
import numpy as np
