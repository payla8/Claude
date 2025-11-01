"""
Market Data API - Autonomous data fetching system
Supports both real exchange data and mock data for testing
"""

import asyncio
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.utils.logger import get_logger


class MarketDataAPI:
    """Advanced market data fetching with multiple sources"""

    def __init__(self, mock_mode: bool = True):
        self.logger = get_logger("MarketDataAPI")
        self.mock_mode = mock_mode
        self.exchanges = {}
        self.cache = {}
        self.cache_duration = 60  # seconds

        if not mock_mode:
            self._initialize_exchanges()

        self.logger.info(f"MarketDataAPI initialized in {'MOCK' if mock_mode else 'LIVE'} mode")

    def _initialize_exchanges(self):
        """Initialize connections to cryptocurrency exchanges"""
        try:
            self.exchanges['binance'] = ccxt.binance({
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
            self.logger.info("Binance exchange connected")
        except Exception as e:
            self.logger.warning(f"Could not connect to Binance: {e}")

        try:
            self.exchanges['coinbase'] = ccxt.coinbase({
                'enableRateLimit': True
            })
            self.logger.info("Coinbase exchange connected")
        except Exception as e:
            self.logger.warning(f"Could not connect to Coinbase: {e}")

    async def get_ticker(self, symbol: str, exchange: str = 'binance') -> Dict[str, Any]:
        """Get current ticker data"""
        if self.mock_mode:
            return self._generate_mock_ticker(symbol)

        cache_key = f"{exchange}_{symbol}_ticker"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']

        try:
            ticker = await self.exchanges[exchange].fetch_ticker(symbol)
            self.cache[cache_key] = {
                'data': ticker,
                'timestamp': datetime.now()
            }
            return ticker
        except Exception as e:
            self.logger.error(f"Error fetching ticker for {symbol}: {e}")
            return self._generate_mock_ticker(symbol)

    async def get_ohlcv(self, symbol: str, timeframe: str = '1h',
                        limit: int = 500, exchange: str = 'binance') -> pd.DataFrame:
        """Get OHLCV (candlestick) data"""
        if self.mock_mode:
            return self._generate_mock_ohlcv(symbol, timeframe, limit)

        try:
            ohlcv = await self.exchanges[exchange].fetch_ohlcv(
                symbol, timeframe, limit=limit
            )
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return self._generate_mock_ohlcv(symbol, timeframe, limit)

    async def get_orderbook(self, symbol: str, exchange: str = 'binance') -> Dict[str, Any]:
        """Get order book data"""
        if self.mock_mode:
            return self._generate_mock_orderbook(symbol)

        try:
            orderbook = await self.exchanges[exchange].fetch_order_book(symbol)
            return orderbook
        except Exception as e:
            self.logger.error(f"Error fetching orderbook for {symbol}: {e}")
            return self._generate_mock_orderbook(symbol)

    async def get_multiple_symbols(self, symbols: List[str],
                                   timeframe: str = '1h') -> Dict[str, pd.DataFrame]:
        """Get data for multiple symbols concurrently"""
        tasks = [self.get_ohlcv(symbol, timeframe) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        return dict(zip(symbols, results))

    def _generate_mock_ticker(self, symbol: str) -> Dict[str, Any]:
        """Generate realistic mock ticker data"""
        # Base prices for different cryptocurrencies
        base_prices = {
            'BTC/USDT': 45000,
            'ETH/USDT': 2500,
            'BNB/USDT': 320,
            'SOL/USDT': 110,
            'ADA/USDT': 0.55,
            'XRP/USDT': 0.62,
            'DOT/USDT': 7.5,
            'MATIC/USDT': 0.85
        }

        base_price = base_prices.get(symbol, 100)
        # Add some randomness
        price = base_price * (1 + np.random.uniform(-0.02, 0.02))

        return {
            'symbol': symbol,
            'timestamp': datetime.now().timestamp() * 1000,
            'datetime': datetime.now().isoformat(),
            'last': price,
            'bid': price * 0.9995,
            'ask': price * 1.0005,
            'high': price * 1.015,
            'low': price * 0.985,
            'open': price * (1 + np.random.uniform(-0.01, 0.01)),
            'close': price,
            'volume': np.random.uniform(1000000, 10000000),
            'change': np.random.uniform(-3, 3),
            'percentage': np.random.uniform(-3, 3),
        }

    def _generate_mock_ohlcv(self, symbol: str, timeframe: str,
                             limit: int) -> pd.DataFrame:
        """Generate realistic mock OHLCV data with trends"""
        base_prices = {
            'BTC/USDT': 45000,
            'ETH/USDT': 2500,
            'BNB/USDT': 320,
            'SOL/USDT': 110,
            'ADA/USDT': 0.55,
            'XRP/USDT': 0.62,
            'DOT/USDT': 7.5,
            'MATIC/USDT': 0.85
        }

        base_price = base_prices.get(symbol, 100)

        # Generate timestamps
        timeframe_minutes = self._timeframe_to_minutes(timeframe)
        end_time = datetime.now()
        timestamps = [
            end_time - timedelta(minutes=timeframe_minutes * i)
            for i in range(limit)
        ]
        timestamps.reverse()

        # Generate price data with realistic movements
        prices = []
        current_price = base_price
        trend = np.random.choice([-1, 0, 1], p=[0.3, 0.4, 0.3])  # down, sideways, up

        for i in range(limit):
            # Add trend component
            trend_component = trend * 0.001
            # Add random walk
            random_walk = np.random.normal(0, 0.002)
            # Occasional trend changes
            if np.random.random() < 0.05:
                trend = np.random.choice([-1, 0, 1], p=[0.3, 0.4, 0.3])

            current_price *= (1 + trend_component + random_walk)
            prices.append(current_price)

        # Generate OHLCV
        data = []
        for i, (ts, close) in enumerate(zip(timestamps, prices)):
            volatility = np.random.uniform(0.005, 0.015)
            open_price = close * (1 + np.random.uniform(-volatility/2, volatility/2))
            high_price = max(open_price, close) * (1 + np.random.uniform(0, volatility))
            low_price = min(open_price, close) * (1 - np.random.uniform(0, volatility))
            volume = np.random.uniform(1000000, 5000000)

            data.append({
                'timestamp': ts,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close,
                'volume': volume
            })

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df

    def _generate_mock_orderbook(self, symbol: str) -> Dict[str, Any]:
        """Generate mock order book"""
        base_price = self._generate_mock_ticker(symbol)['last']

        # Generate bids (buy orders)
        bids = []
        for i in range(20):
            price = base_price * (1 - (i + 1) * 0.0005)
            amount = np.random.uniform(0.1, 10)
            bids.append([price, amount])

        # Generate asks (sell orders)
        asks = []
        for i in range(20):
            price = base_price * (1 + (i + 1) * 0.0005)
            amount = np.random.uniform(0.1, 10)
            asks.append([price, amount])

        return {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'timestamp': datetime.now().timestamp() * 1000,
            'datetime': datetime.now().isoformat()
        }

    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        multipliers = {'m': 1, 'h': 60, 'd': 1440, 'w': 10080}
        return int(timeframe[:-1]) * multipliers.get(timeframe[-1], 60)

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False

        cache_time = self.cache[key]['timestamp']
        age = (datetime.now() - cache_time).seconds
        return age < self.cache_duration


# Global instance
_market_data_api = None


def get_market_data_api(mock_mode: bool = True) -> MarketDataAPI:
    """Get global market data API instance"""
    global _market_data_api
    if _market_data_api is None:
        _market_data_api = MarketDataAPI(mock_mode=mock_mode)
    return _market_data_api
