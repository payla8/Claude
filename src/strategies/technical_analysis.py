"""
Advanced Technical Analysis Engine
Implements multiple indicators and pattern recognition
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TechnicalIndicators:
    """Container for technical indicators"""
    rsi: Optional[float] = None
    macd: Optional[Dict[str, float]] = None
    bollinger_bands: Optional[Dict[str, float]] = None
    stochastic: Optional[Dict[str, float]] = None
    adx: Optional[float] = None
    atr: Optional[float] = None
    obv: Optional[float] = None
    cci: Optional[float] = None
    williams_r: Optional[float] = None
    moving_averages: Optional[Dict[str, float]] = None
    vwap: Optional[float] = None


class TechnicalAnalysisEngine:
    """Advanced technical analysis with multiple indicators"""

    def __init__(self):
        self.indicators = {}

    def calculate_all_indicators(self, df: pd.DataFrame) -> TechnicalIndicators:
        """Calculate all technical indicators"""
        indicators = TechnicalIndicators()

        indicators.rsi = self.calculate_rsi(df)
        indicators.macd = self.calculate_macd(df)
        indicators.bollinger_bands = self.calculate_bollinger_bands(df)
        indicators.stochastic = self.calculate_stochastic(df)
        indicators.adx = self.calculate_adx(df)
        indicators.atr = self.calculate_atr(df)
        indicators.obv = self.calculate_obv(df)
        indicators.cci = self.calculate_cci(df)
        indicators.williams_r = self.calculate_williams_r(df)
        indicators.moving_averages = self.calculate_moving_averages(df)
        indicators.vwap = self.calculate_vwap(df)

        return indicators

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

    def calculate_macd(self, df: pd.DataFrame,
                       fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()

        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return {
            'macd': float(macd.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }

    def calculate_bollinger_bands(self, df: pd.DataFrame,
                                  period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        current_price = df['close'].iloc[-1]
        bb_position = (current_price - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])

        return {
            'upper': float(upper_band.iloc[-1]),
            'middle': float(sma.iloc[-1]),
            'lower': float(lower_band.iloc[-1]),
            'position': float(bb_position),  # 0 = at lower, 1 = at upper
            'width': float((upper_band.iloc[-1] - lower_band.iloc[-1]) / sma.iloc[-1])
        }

    def calculate_stochastic(self, df: pd.DataFrame,
                            k_period: int = 14, d_period: int = 3) -> Dict[str, float]:
        """Calculate Stochastic Oscillator"""
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()

        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()

        return {
            'k': float(k_percent.iloc[-1]),
            'd': float(d_percent.iloc[-1])
        }

    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average Directional Index (trend strength)"""
        high = df['high']
        low = df['low']
        close = df['close']

        plus_dm = high.diff()
        minus_dm = low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0

        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        tr = pd.concat([tr1, tr2, tr3], axis=1, join='inner').max(axis=1)

        atr = tr.rolling(window=period).mean()

        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = abs(100 * (minus_dm.rolling(window=period).mean() / atr))

        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.rolling(window=period).mean()

        return float(adx.iloc[-1])

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range (volatility)"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(period).mean()

        return float(atr.iloc[-1])

    def calculate_obv(self, df: pd.DataFrame) -> float:
        """Calculate On-Balance Volume"""
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        return float(obv.iloc[-1])

    def calculate_cci(self, df: pd.DataFrame, period: int = 20) -> float:
        """Calculate Commodity Channel Index"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())

        cci = (tp - sma) / (0.015 * mad)
        return float(cci.iloc[-1])

    def calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Williams %R"""
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()

        williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
        return float(williams_r.iloc[-1])

    def calculate_moving_averages(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate various moving averages"""
        return {
            'sma_20': float(df['close'].rolling(window=20).mean().iloc[-1]),
            'sma_50': float(df['close'].rolling(window=50).mean().iloc[-1]),
            'sma_200': float(df['close'].rolling(window=200).mean().iloc[-1]),
            'ema_12': float(df['close'].ewm(span=12, adjust=False).mean().iloc[-1]),
            'ema_26': float(df['close'].ewm(span=26, adjust=False).mean().iloc[-1]),
        }

    def calculate_vwap(self, df: pd.DataFrame) -> float:
        """Calculate Volume Weighted Average Price"""
        vwap = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
        return float(vwap.iloc[-1])

    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Detect common chart patterns"""
        patterns = {}

        # Golden Cross / Death Cross
        sma_50 = df['close'].rolling(window=50).mean()
        sma_200 = df['close'].rolling(window=200).mean()

        if len(df) >= 200:
            patterns['golden_cross'] = (sma_50.iloc[-1] > sma_200.iloc[-1] and
                                       sma_50.iloc[-2] <= sma_200.iloc[-2])
            patterns['death_cross'] = (sma_50.iloc[-1] < sma_200.iloc[-1] and
                                      sma_50.iloc[-2] >= sma_200.iloc[-2])
        else:
            patterns['golden_cross'] = False
            patterns['death_cross'] = False

        # Bullish/Bearish Engulfing
        if len(df) >= 2:
            patterns['bullish_engulfing'] = (
                df['close'].iloc[-2] < df['open'].iloc[-2] and
                df['close'].iloc[-1] > df['open'].iloc[-1] and
                df['close'].iloc[-1] > df['open'].iloc[-2] and
                df['open'].iloc[-1] < df['close'].iloc[-2]
            )

            patterns['bearish_engulfing'] = (
                df['close'].iloc[-2] > df['open'].iloc[-2] and
                df['close'].iloc[-1] < df['open'].iloc[-1] and
                df['close'].iloc[-1] < df['open'].iloc[-2] and
                df['open'].iloc[-1] > df['close'].iloc[-2]
            )
        else:
            patterns['bullish_engulfing'] = False
            patterns['bearish_engulfing'] = False

        # Hammer and Shooting Star
        if len(df) >= 1:
            body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
            range_size = df['high'].iloc[-1] - df['low'].iloc[-1]

            if range_size > 0:
                lower_shadow = min(df['open'].iloc[-1], df['close'].iloc[-1]) - df['low'].iloc[-1]
                upper_shadow = df['high'].iloc[-1] - max(df['open'].iloc[-1], df['close'].iloc[-1])

                patterns['hammer'] = (lower_shadow > 2 * body and upper_shadow < body)
                patterns['shooting_star'] = (upper_shadow > 2 * body and lower_shadow < body)
            else:
                patterns['hammer'] = False
                patterns['shooting_star'] = False
        else:
            patterns['hammer'] = False
            patterns['shooting_star'] = False

        return patterns

    def get_signal_strength(self, indicators: TechnicalIndicators,
                          patterns: Dict[str, bool]) -> Dict[str, float]:
        """Calculate overall signal strength"""
        bullish_score = 0
        bearish_score = 0
        total_signals = 0

        # RSI signals
        if indicators.rsi is not None:
            total_signals += 1
            if indicators.rsi < 30:
                bullish_score += 1
            elif indicators.rsi > 70:
                bearish_score += 1

        # MACD signals
        if indicators.macd is not None:
            total_signals += 1
            if indicators.macd['histogram'] > 0:
                bullish_score += 1
            else:
                bearish_score += 1

        # Bollinger Bands
        if indicators.bollinger_bands is not None:
            total_signals += 1
            if indicators.bollinger_bands['position'] < 0.2:
                bullish_score += 1
            elif indicators.bollinger_bands['position'] > 0.8:
                bearish_score += 1

        # Stochastic
        if indicators.stochastic is not None:
            total_signals += 1
            if indicators.stochastic['k'] < 20:
                bullish_score += 1
            elif indicators.stochastic['k'] > 80:
                bearish_score += 1

        # ADX (trend strength, not direction)
        trend_strength = 0
        if indicators.adx is not None:
            trend_strength = min(indicators.adx / 50, 1.0)  # Normalize to 0-1

        # Pattern signals
        if patterns.get('golden_cross') or patterns.get('bullish_engulfing') or patterns.get('hammer'):
            bullish_score += 1
            total_signals += 1

        if patterns.get('death_cross') or patterns.get('bearish_engulfing') or patterns.get('shooting_star'):
            bearish_score += 1
            total_signals += 1

        # Calculate normalized scores
        if total_signals > 0:
            bullish_strength = (bullish_score / total_signals) * trend_strength
            bearish_strength = (bearish_score / total_signals) * trend_strength
        else:
            bullish_strength = 0
            bearish_strength = 0

        return {
            'bullish': bullish_strength,
            'bearish': bearish_strength,
            'neutral': 1 - (bullish_strength + bearish_strength),
            'trend_strength': trend_strength
        }
