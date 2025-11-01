"""
Crypto Investment AI Bot - Main Orchestrator
Advanced Multi-Agent AI System for Cryptocurrency Trading
"""

import asyncio
import signal
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.config_loader import get_config
from src.data.market_data_api import get_market_data_api
from src.agents.coordinator_agent import CoordinatorAgent
from src.exchange.trading_engine import TradingEngine
from src.portfolio.portfolio_manager import PortfolioManager


class CryptoTradingBot:
    """
    Main AI Trading Bot Orchestrator

    This bot coordinates multiple specialized AI agents to analyze cryptocurrency
    markets and make intelligent trading decisions.
    """

    def __init__(self):
        self.logger = get_logger("CryptoBot")
        self.config = get_config()

        # Initialize components
        self.logger.info("=" * 80)
        self.logger.info("INITIALIZING CRYPTO INVESTMENT AI BOT")
        self.logger.info("=" * 80)

        # Market Data
        trading_mode = self.config.get('trading.mode', 'paper')
        mock_mode = trading_mode == 'paper'
        self.market_data = get_market_data_api(mock_mode=mock_mode)
        self.logger.info(f"Market Data API initialized (mode: {trading_mode})")

        # AI Coordinator (manages all specialized agents)
        self.coordinator = CoordinatorAgent(self.config.get_all())
        self.logger.info("AI Coordinator initialized with multi-agent system")

        # Trading Engine
        self.trading_engine = TradingEngine(
            self.config.get_all(),
            paper_trading=(trading_mode == 'paper')
        )
        self.logger.info(f"Trading Engine initialized ({trading_mode} mode)")

        # Portfolio Manager
        initial_capital = self.config.get('capital.initial', 10000)
        self.portfolio = PortfolioManager(initial_capital)
        self.logger.info(f"Portfolio Manager initialized with ${initial_capital:,.2f}")

        # Bot state
        self.running = False
        self.symbols = self.config.get('trading.symbols', ['BTC/USDT', 'ETH/USDT'])
        self.analysis_interval = 300  # 5 minutes default
        self.trade_count = 0
        self.start_time = None

        # Performance tracking
        self.performance_log = []
        self.decisions_log = []

    async def start(self):
        """Start the trading bot"""
        self.logger.info("=" * 80)
        self.logger.info("🤖 CRYPTO AI BOT STARTED")
        self.logger.info("=" * 80)
        self.logger.info(f"Trading Mode: {self.config.get('trading.mode', 'paper').upper()}")
        self.logger.info(f"Monitoring Symbols: {', '.join(self.symbols)}")
        self.logger.info(f"Initial Capital: ${self.portfolio.initial_capital:,.2f}")
        self.logger.info(f"Analysis Interval: {self.analysis_interval}s")
        self.logger.info("=" * 80)

        self.running = True
        self.start_time = datetime.now()

        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Display agent status
        self._display_agent_status()

        # Main bot loop
        try:
            await self._main_loop()
        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}", exc_info=True)
        finally:
            await self.stop()

    async def _main_loop(self):
        """Main trading loop"""
        cycle_count = 0

        while self.running:
            cycle_count += 1
            cycle_start = datetime.now()

            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info(f"ANALYSIS CYCLE #{cycle_count}")
            self.logger.info(f"Time: {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info("=" * 80)

            # Update portfolio prices
            await self._update_portfolio_prices()

            # Display portfolio status
            self._display_portfolio_status()

            # Analyze each symbol
            for symbol in self.symbols:
                try:
                    await self._analyze_and_trade(symbol)
                except Exception as e:
                    self.logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)

            # Display summary
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            self.logger.info(f"Cycle completed in {cycle_duration:.2f}s")
            self.logger.info(f"Next analysis in {self.analysis_interval}s")

            # Wait for next cycle
            await asyncio.sleep(self.analysis_interval)

    async def _analyze_and_trade(self, symbol: str):
        """Analyze market and execute trades for a symbol"""
        self.logger.info(f"\n--- Analyzing {symbol} ---")

        # Get portfolio data
        portfolio_data = {
            'value': self.portfolio.get_portfolio_value(),
            'positions': self.portfolio.get_positions()
        }

        # Get trading decision from AI coordinator
        decision = await self.coordinator.generate_trading_decision(
            symbol=symbol,
            market_data_api=self.market_data,
            portfolio_data=portfolio_data
        )

        # Log decision
        if decision:
            self.decisions_log.append(decision)
            self._display_decision(decision)

            # Execute trade if decision is not HOLD
            if decision['action'] != 'HOLD':
                # Check if we should execute based on confidence
                min_confidence = self.config.get('min_confidence_threshold', 0.7)

                if decision['confidence'] >= min_confidence:
                    await self._execute_decision(decision)
                else:
                    self.logger.info(
                        f"Decision confidence ({decision['confidence']:.2%}) "
                        f"below threshold ({min_confidence:.0%}) - skipping trade"
                    )
        else:
            self.logger.info(f"No trading decision for {symbol}")

    async def _execute_decision(self, decision: Dict[str, Any]):
        """Execute a trading decision"""
        symbol = decision['symbol']
        action = decision['action']
        current_price = decision['current_price']

        # Check if we already have a position
        has_position = self.portfolio.has_position(symbol)

        if action == 'BUY' and not has_position:
            # Execute buy
            result = await self.trading_engine.execute_trade(
                decision=decision,
                portfolio_value=self.portfolio.get_portfolio_value()
            )

            if result and result['status'].value == 'filled':
                # Add position to portfolio
                self.portfolio.add_position(
                    symbol=symbol,
                    quantity=result['filled_quantity'],
                    price=result['filled_price'],
                    side='long',
                    stop_loss=decision.get('stop_loss'),
                    take_profit=decision.get('take_profit')
                )
                self.trade_count += 1

        elif action == 'SELL' and has_position:
            # Execute sell
            position = self.portfolio.get_position(symbol)
            result = await self.trading_engine.execute_trade(
                decision=decision,
                portfolio_value=self.portfolio.get_portfolio_value()
            )

            if result and result['status'].value == 'filled':
                # Close position
                closed = self.portfolio.close_position(symbol, result['filled_price'])
                if closed:
                    self.logger.info(
                        f"Position closed - PnL: ${closed['pnl']:.2f} "
                        f"({closed['pnl_percentage']:.2f}%)"
                    )
                self.trade_count += 1

    async def _update_portfolio_prices(self):
        """Update current prices for all positions"""
        if not self.portfolio.positions:
            return

        prices = {}
        for symbol in self.portfolio.positions.keys():
            try:
                ticker = await self.market_data.get_ticker(symbol)
                prices[symbol] = ticker['last']
            except Exception as e:
                self.logger.error(f"Error updating price for {symbol}: {e}")

        self.portfolio.update_prices(prices)

    def _display_portfolio_status(self):
        """Display current portfolio status"""
        metrics = self.portfolio.get_performance_metrics()

        self.logger.info("\n📊 PORTFOLIO STATUS")
        self.logger.info("-" * 60)
        self.logger.info(f"Total Value:      ${metrics['current_value']:,.2f}")
        self.logger.info(f"Cash:             ${metrics['cash']:,.2f}")
        self.logger.info(f"Positions Value:  ${metrics['positions_value']:,.2f}")
        self.logger.info(f"Total P&L:        ${metrics['total_pnl']:,.2f} ({metrics['total_return_pct']:+.2f}%)")
        self.logger.info(f"Open Positions:   {metrics['open_positions']}")
        self.logger.info(f"Total Trades:     {metrics['total_trades']}")
        if metrics['total_trades'] > 0:
            self.logger.info(f"Win Rate:         {metrics['win_rate']:.1f}%")
            self.logger.info(f"Profit Factor:    {metrics['profit_factor']:.2f}")

        # Display open positions
        if self.portfolio.positions:
            self.logger.info("\n📈 OPEN POSITIONS")
            self.logger.info("-" * 60)
            for symbol, position in self.portfolio.positions.items():
                self.logger.info(
                    f"{symbol}: {position.quantity:.6f} @ ${position.entry_price:.2f} | "
                    f"Current: ${position.current_price:.2f} | "
                    f"P&L: ${position.pnl:+.2f} ({position.pnl_percentage:+.2f}%)"
                )

    def _display_decision(self, decision: Dict[str, Any]):
        """Display trading decision"""
        self.logger.info("\n🤖 AI DECISION")
        self.logger.info("-" * 60)
        self.logger.info(f"Action:       {decision['action']} ({decision['strength']})")
        self.logger.info(f"Confidence:   {decision['confidence']:.2%}")
        self.logger.info(f"Consensus:    {decision['consensus_score']:.2%}")
        self.logger.info(f"Price:        ${decision['current_price']:.2f}")

        if decision.get('stop_loss'):
            self.logger.info(f"Stop Loss:    {decision['stop_loss']:.2%}")
        if decision.get('take_profit'):
            self.logger.info(f"Take Profit:  {decision['take_profit']:.2%}")

        self.logger.info("\nAgent Reasoning:")
        for i, reasoning in enumerate(decision['reasoning'][:3], 1):
            self.logger.info(f"  {i}. {reasoning}")

    def _display_agent_status(self):
        """Display status of all AI agents"""
        status = self.coordinator.get_agent_status()

        self.logger.info("\n🧠 AI AGENTS STATUS")
        self.logger.info("-" * 60)
        for agent_name, agent_info in status.items():
            self.logger.info(
                f"{agent_name.upper()}: "
                f"Active={agent_info['active']}, "
                f"Weight={agent_info['weight']:.2%}, "
                f"Accuracy={agent_info['performance']['accuracy_rate']:.2%}"
            )

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("\n\nShutdown signal received...")
        self.running = False

    async def stop(self):
        """Stop the bot gracefully"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("🛑 STOPPING CRYPTO AI BOT")
        self.logger.info("=" * 80)

        # Display final statistics
        if self.start_time:
            runtime = datetime.now() - self.start_time
            self.logger.info(f"Runtime: {runtime}")

        self.logger.info(f"Total Trades Executed: {self.trade_count}")

        # Final portfolio status
        self._display_portfolio_status()

        # Close all positions (optional)
        # await self._close_all_positions()

        self.logger.info("\n✅ Bot stopped gracefully")
        self.logger.info("=" * 80)


async def main():
    """Main entry point"""
    bot = CryptoTradingBot()
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nBot interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
