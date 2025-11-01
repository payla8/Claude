"""
Pattern Recognition Agent - Expert in chart patterns and price action
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from .base_agent import BaseAgent, AgentSignal, MarketAnalysis


class PatternRecognitionAgent(BaseAgent):
    """Agent specialized in pattern recognition"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("PatternRecognition", config)
        self.expertise_areas = [
            'Chart Patterns', 'Candlestick Patterns', 'Support/Resistance',
            'Fibonacci Levels', 'Elliott Waves', 'Price Action'
        ]

    async def analyze(self, market_data: Dict[str, Any]) -> MarketAnalysis:
        """Analyze market for patterns"""
        df = market_data['df']
        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')

        # Detect various patterns
        chart_patterns = self._detect_chart_patterns(df)
        candlestick_patterns = self._detect_candlestick_patterns(df)
        support_resistance = self._find_support_resistance(df)
        fibonacci_levels = self._calculate_fibonacci_levels(df)

        # Calculate pattern strength
        pattern_strength = self._calculate_pattern_strength(
            chart_patterns, candlestick_patterns
        )

        # Determine risk and opportunity
        risk_level = self._calculate_risk_level(df, support_resistance)
        opportunity_score = pattern_strength

        analysis = {
            'chart_patterns': chart_patterns,
            'candlestick_patterns': candlestick_patterns,
            'support_resistance': support_resistance,
            'fibonacci_levels': fibonacci_levels,
            'pattern_strength': pattern_strength,
            'price_action': self._analyze_price_action(df)
        }

        confidence_factors = {
            'data_quality': 1.0 if len(df) >= 100 else len(df) / 100,
            'signal_strength': pattern_strength,
            'market_conditions': 0.8,
            'historical_accuracy': self.performance_metrics['accuracy_rate']
        }

        confidence = self._calculate_confidence(confidence_factors)

        return MarketAnalysis(
            agent_name=self.name,
            timestamp=datetime.now(),
            symbol=symbol,
            analysis=analysis,
            risk_level=risk_level,
            opportunity_score=opportunity_score,
            timeframe=timeframe,
            confidence=confidence
        )

    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[AgentSignal]:
        """Generate signal based on pattern recognition"""
        analysis = await self.analyze(market_data)

        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')

        # Check if pattern strength is sufficient
        if analysis.analysis['pattern_strength'] < 0.5:
            return None

        chart_patterns = analysis.analysis['chart_patterns']
        candlestick_patterns = analysis.analysis['candlestick_patterns']

        # Determine signal direction
        bullish_score = 0
        bearish_score = 0

        for pattern, detected in chart_patterns.items():
            if detected:
                if pattern in ['head_and_shoulders_bottom', 'double_bottom', 'ascending_triangle']:
                    bullish_score += 1
                elif pattern in ['head_and_shoulders_top', 'double_top', 'descending_triangle']:
                    bearish_score += 1

        for pattern, detected in candlestick_patterns.items():
            if detected:
                if pattern in ['bullish_engulfing', 'hammer', 'morning_star']:
                    bullish_score += 1
                elif pattern in ['bearish_engulfing', 'shooting_star', 'evening_star']:
                    bearish_score += 1

        if bullish_score == bearish_score:
            return None

        net_score = (bullish_score - bearish_score) / max(bullish_score + bearish_score, 1)
        signal_type = self._get_signal_type(0.5 + net_score / 2)

        # Build reasoning
        reasoning_parts = []
        active_patterns = [p for p, v in chart_patterns.items() if v]
        active_candlesticks = [p for p, v in candlestick_patterns.items() if v]

        if active_patterns:
            reasoning_parts.append(f"Chart patterns: {', '.join(active_patterns)}")
        if active_candlesticks:
            reasoning_parts.append(f"Candlestick patterns: {', '.join(active_candlesticks)}")

        support_resistance = analysis.analysis['support_resistance']
        if support_resistance['near_support']:
            reasoning_parts.append("Price near support level")
        if support_resistance['near_resistance']:
            reasoning_parts.append("Price near resistance level")

        reasoning = "; ".join(reasoning_parts)

        priority = int(5 + (analysis.analysis['pattern_strength'] * 5))

        return AgentSignal(
            agent_name=self.name,
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal_type,
            confidence=analysis.confidence,
            reasoning=reasoning,
            data={
                'patterns': analysis.analysis
            },
            timeframe=timeframe,
            priority=priority
        )

    def _detect_chart_patterns(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Detect major chart patterns"""
        patterns = {}

        if len(df) < 50:
            return {
                'head_and_shoulders_top': False,
                'head_and_shoulders_bottom': False,
                'double_top': False,
                'double_bottom': False,
                'ascending_triangle': False,
                'descending_triangle': False,
                'symmetrical_triangle': False
            }

        # Simplified pattern detection (in production, would use more sophisticated algorithms)
        prices = df['close'].values[-50:]
        highs = df['high'].values[-50:]
        lows = df['low'].values[-50:]

        # Double top/bottom detection
        peaks = self._find_peaks(prices)
        if len(peaks) >= 2:
            if abs(prices[peaks[-1]] - prices[peaks[-2]]) / prices[peaks[-1]] < 0.02:
                patterns['double_top'] = prices[peaks[-1]] > np.mean(prices)
                patterns['double_bottom'] = prices[peaks[-1]] < np.mean(prices)
            else:
                patterns['double_top'] = False
                patterns['double_bottom'] = False
        else:
            patterns['double_top'] = False
            patterns['double_bottom'] = False

        # Triangle patterns (simplified)
        recent_highs = highs[-20:]
        recent_lows = lows[-20:]

        high_trend = np.polyfit(range(len(recent_highs)), recent_highs, 1)[0]
        low_trend = np.polyfit(range(len(recent_lows)), recent_lows, 1)[0]

        patterns['ascending_triangle'] = high_trend < 0.0001 and low_trend > 0
        patterns['descending_triangle'] = high_trend < 0 and low_trend > -0.0001
        patterns['symmetrical_triangle'] = high_trend < 0 and low_trend > 0

        # Head and shoulders (simplified)
        patterns['head_and_shoulders_top'] = False
        patterns['head_and_shoulders_bottom'] = False

        return patterns

    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Detect candlestick patterns"""
        if len(df) < 3:
            return {
                'bullish_engulfing': False,
                'bearish_engulfing': False,
                'hammer': False,
                'shooting_star': False,
                'doji': False,
                'morning_star': False,
                'evening_star': False
            }

        patterns = {}

        # Get last few candles
        o = df['open'].values
        h = df['high'].values
        l = df['low'].values
        c = df['close'].values

        # Bullish/Bearish Engulfing
        if len(df) >= 2:
            patterns['bullish_engulfing'] = (
                c[-2] < o[-2] and c[-1] > o[-1] and
                c[-1] > o[-2] and o[-1] < c[-2]
            )
            patterns['bearish_engulfing'] = (
                c[-2] > o[-2] and c[-1] < o[-1] and
                c[-1] < o[-2] and o[-1] > c[-2]
            )
        else:
            patterns['bullish_engulfing'] = False
            patterns['bearish_engulfing'] = False

        # Hammer and Shooting Star
        body = abs(c[-1] - o[-1])
        range_size = h[-1] - l[-1]

        if range_size > 0:
            lower_shadow = min(o[-1], c[-1]) - l[-1]
            upper_shadow = h[-1] - max(o[-1], c[-1])

            patterns['hammer'] = lower_shadow > 2 * body and upper_shadow < body
            patterns['shooting_star'] = upper_shadow > 2 * body and lower_shadow < body
        else:
            patterns['hammer'] = False
            patterns['shooting_star'] = False

        # Doji
        patterns['doji'] = body / range_size < 0.1 if range_size > 0 else False

        # Morning/Evening Star
        if len(df) >= 3:
            patterns['morning_star'] = (
                c[-3] < o[-3] and
                abs(c[-2] - o[-2]) < body and
                c[-1] > o[-1] and c[-1] > (o[-3] + c[-3]) / 2
            )
            patterns['evening_star'] = (
                c[-3] > o[-3] and
                abs(c[-2] - o[-2]) < body and
                c[-1] < o[-1] and c[-1] < (o[-3] + c[-3]) / 2
            )
        else:
            patterns['morning_star'] = False
            patterns['evening_star'] = False

        return patterns

    def _find_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Find support and resistance levels"""
        if len(df) < 20:
            return {
                'support_levels': [],
                'resistance_levels': [],
                'near_support': False,
                'near_resistance': False
            }

        prices = df['close'].values
        current_price = prices[-1]

        # Find local extrema
        support_levels = []
        resistance_levels = []

        window = 10
        for i in range(window, len(prices) - window):
            if prices[i] == min(prices[i-window:i+window]):
                support_levels.append(prices[i])
            if prices[i] == max(prices[i-window:i+window]):
                resistance_levels.append(prices[i])

        # Keep only recent and significant levels
        support_levels = sorted(set(support_levels))[-5:]
        resistance_levels = sorted(set(resistance_levels))[-5:]

        # Check if near support/resistance
        near_support = any(abs(current_price - level) / current_price < 0.02 for level in support_levels)
        near_resistance = any(abs(current_price - level) / current_price < 0.02 for level in resistance_levels)

        return {
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'near_support': near_support,
            'near_resistance': near_resistance
        }

    def _calculate_fibonacci_levels(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        if len(df) < 50:
            return {}

        prices = df['close'].values[-50:]
        high = max(prices)
        low = min(prices)
        diff = high - low

        return {
            'level_0': high,
            'level_236': high - 0.236 * diff,
            'level_382': high - 0.382 * diff,
            'level_500': high - 0.500 * diff,
            'level_618': high - 0.618 * diff,
            'level_100': low
        }

    def _find_peaks(self, prices: np.ndarray, distance: int = 5) -> list:
        """Find peaks in price data"""
        peaks = []
        for i in range(distance, len(prices) - distance):
            if prices[i] == max(prices[i-distance:i+distance+1]):
                peaks.append(i)
        return peaks

    def _calculate_pattern_strength(self, chart_patterns: Dict[str, bool],
                                   candlestick_patterns: Dict[str, bool]) -> float:
        """Calculate overall pattern strength"""
        total_patterns = len(chart_patterns) + len(candlestick_patterns)
        detected_patterns = sum(chart_patterns.values()) + sum(candlestick_patterns.values())

        if total_patterns == 0:
            return 0.0

        return detected_patterns / total_patterns

    def _calculate_risk_level(self, df: pd.DataFrame,
                             support_resistance: Dict[str, Any]) -> float:
        """Calculate risk level based on proximity to support/resistance"""
        if support_resistance['near_support']:
            return 0.3  # Lower risk near support
        elif support_resistance['near_resistance']:
            return 0.7  # Higher risk near resistance
        else:
            return 0.5

    def _analyze_price_action(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze recent price action"""
        if len(df) < 5:
            return {'momentum': 'neutral', 'volatility': 'low'}

        recent_closes = df['close'].values[-5:]
        returns = np.diff(recent_closes) / recent_closes[:-1]

        avg_return = np.mean(returns)
        volatility = np.std(returns)

        momentum = 'bullish' if avg_return > 0.01 else 'bearish' if avg_return < -0.01 else 'neutral'
        vol_label = 'high' if volatility > 0.03 else 'medium' if volatility > 0.01 else 'low'

        return {
            'momentum': momentum,
            'volatility': vol_label,
            'avg_return': float(avg_return),
            'volatility_value': float(volatility)
        }
