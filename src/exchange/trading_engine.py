"""
Trading Execution Engine - Executes trades based on agent decisions
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import uuid
from src.utils.logger import get_logger


class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class TradingEngine:
    """Executes and manages trades"""

    def __init__(self, config: Dict[str, Any], paper_trading: bool = True):
        self.config = config
        self.paper_trading = paper_trading
        self.logger = get_logger("TradingEngine")

        self.orders = {}
        self.trade_history = []

        mode = "PAPER TRADING" if paper_trading else "LIVE TRADING"
        self.logger.info(f"TradingEngine initialized in {mode} mode")

    async def execute_trade(self, decision: Dict[str, Any],
                          portfolio_value: float) -> Optional[Dict[str, Any]]:
        """Execute a trade based on coordinator decision"""
        if decision['action'] == 'HOLD':
            self.logger.info(f"Decision is HOLD for {decision['symbol']} - no trade executed")
            return None

        symbol = decision['symbol']
        action = decision['action']
        current_price = decision['current_price']

        # Calculate position size
        position_size = decision.get('recommended_position_size', portfolio_value * 0.1)

        # Calculate quantity
        quantity = position_size / current_price

        # Create order
        order = self._create_order(
            symbol=symbol,
            side='buy' if action == 'BUY' else 'sell',
            quantity=quantity,
            price=current_price,
            order_type=OrderType.MARKET,
            stop_loss=decision.get('stop_loss'),
            take_profit=decision.get('take_profit'),
            decision_data=decision
        )

        # Execute order
        if self.paper_trading:
            result = await self._execute_paper_order(order)
        else:
            result = await self._execute_live_order(order)

        if result['status'] == OrderStatus.FILLED:
            self.logger.info(
                f"Trade executed: {action} {quantity:.6f} {symbol} @ {current_price:.2f} "
                f"(Total: ${position_size:.2f})"
            )

            # Set stop loss and take profit orders
            if decision.get('stop_loss'):
                await self._set_stop_loss(symbol, quantity, current_price, decision['stop_loss'])

            if decision.get('take_profit'):
                await self._set_take_profit(symbol, quantity, current_price, decision['take_profit'])

        return result

    def _create_order(self, symbol: str, side: str, quantity: float,
                     price: float, order_type: OrderType,
                     stop_loss: Optional[float] = None,
                     take_profit: Optional[float] = None,
                     decision_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Create an order object"""
        order_id = str(uuid.uuid4())

        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'type': order_type,
            'status': OrderStatus.PENDING,
            'created_at': datetime.now(),
            'filled_at': None,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'decision_data': decision_data
        }

        self.orders[order_id] = order
        return order

    async def _execute_paper_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Execute order in paper trading mode (simulated)"""
        # Simulate immediate fill for market orders
        order['status'] = OrderStatus.FILLED
        order['filled_at'] = datetime.now()
        order['filled_price'] = order['price']
        order['filled_quantity'] = order['quantity']

        # Add to trade history
        trade_record = {
            'id': order['id'],
            'timestamp': order['filled_at'],
            'symbol': order['symbol'],
            'side': order['side'],
            'quantity': order['filled_quantity'],
            'price': order['filled_price'],
            'total_value': order['filled_price'] * order['filled_quantity'],
            'mode': 'paper'
        }

        self.trade_history.append(trade_record)

        return {
            'order_id': order['id'],
            'status': order['status'],
            'filled_price': order['filled_price'],
            'filled_quantity': order['filled_quantity'],
            'trade_record': trade_record
        }

    async def _execute_live_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Execute order on live exchange (would integrate with real exchange API)"""
        # In production, would use exchange API (ccxt, etc.)
        self.logger.warning("Live trading not implemented - use paper trading mode")
        return await self._execute_paper_order(order)

    async def _set_stop_loss(self, symbol: str, quantity: float,
                            entry_price: float, stop_loss_pct: float):
        """Set stop loss order"""
        stop_price = entry_price * (1 - stop_loss_pct)

        stop_order = self._create_order(
            symbol=symbol,
            side='sell',
            quantity=quantity,
            price=stop_price,
            order_type=OrderType.STOP_LOSS
        )

        self.logger.info(
            f"Stop loss set for {symbol} at {stop_price:.2f} "
            f"({stop_loss_pct:.1%} below entry)"
        )

        return stop_order

    async def _set_take_profit(self, symbol: str, quantity: float,
                              entry_price: float, take_profit_pct: float):
        """Set take profit order"""
        target_price = entry_price * (1 + take_profit_pct)

        tp_order = self._create_order(
            symbol=symbol,
            side='sell',
            quantity=quantity,
            price=target_price,
            order_type=OrderType.TAKE_PROFIT
        )

        self.logger.info(
            f"Take profit set for {symbol} at {target_price:.2f} "
            f"({take_profit_pct:.1%} above entry)"
        )

        return tp_order

    def get_open_orders(self) -> List[Dict[str, Any]]:
        """Get all open orders"""
        return [
            order for order in self.orders.values()
            if order['status'] in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]
        ]

    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get trade history"""
        return self.trade_history.copy()

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get specific order"""
        return self.orders.get(order_id)

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        order = self.orders.get(order_id)
        if order and order['status'] == OrderStatus.PENDING:
            order['status'] = OrderStatus.CANCELLED
            self.logger.info(f"Order {order_id} cancelled")
            return True
        return False
