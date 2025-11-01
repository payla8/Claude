"""
Technical Analysis Agent - Expert in technical indicators and market analysis
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
from .base_agent import BaseAgent, AgentSignal, MarketAnalysis
from src.strategies.technical_analysis import TechnicalAnalysisEngine


class TechnicalAnalysisAgent(BaseAgent):
    """Agent specialized in technical analysis"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("TechnicalAnalyst", config)
        self.ta_engine = TechnicalAnalysisEngine()
        self.expertise_areas = [
            'RSI', 'MACD', 'Bollinger Bands', 'Stochastic',
            'ADX', 'Moving Averages', 'Volume Analysis'
        ]

    async def analyze(self, market_data: Dict[str, Any]) -> MarketAnalysis:
        """Analyze market using technical indicators"""
        df = market_data['df']
        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')

        # Calculate all indicators
        indicators = self.ta_engine.calculate_all_indicators(df)
        patterns = self.ta_engine.detect_patterns(df)
        signal_strength = self.ta_engine.get_signal_strength(indicators, patterns)

        # Determine risk level based on volatility
        atr_normalized = indicators.atr / df['close'].iloc[-1]
        risk_level = min(atr_normalized * 10, 1.0)  # Normalize ATR to 0-1

        # Calculate opportunity score
        opportunity_score = max(signal_strength['bullish'], signal_strength['bearish'])

        # Build analysis
        analysis = {
            'indicators': {
                'rsi': indicators.rsi,
                'macd': indicators.macd,
                'bollinger_bands': indicators.bollinger_bands,
                'stochastic': indicators.stochastic,
                'adx': indicators.adx,
                'atr': indicators.atr,
                'moving_averages': indicators.moving_averages
            },
            'patterns': patterns,
            'signal_strength': signal_strength,
            'trend': self._determine_trend(df, indicators),
            'volatility': 'high' if risk_level > 0.6 else 'medium' if risk_level > 0.3 else 'low'
        }

        # Calculate confidence
        confidence_factors = {
            'data_quality': 1.0 if len(df) >= 200 else len(df) / 200,
            'signal_strength': signal_strength['trend_strength'],
            'market_conditions': 1.0 - risk_level,
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
        """Generate trading signal based on technical analysis"""
        analysis = await self.analyze(market_data)

        df = market_data['df']
        symbol = market_data['symbol']
        timeframe = market_data.get('timeframe', '1h')

        signal_strength = analysis.analysis['signal_strength']
        indicators = analysis.analysis['indicators']

        # Calculate net signal (bullish - bearish)
        net_signal = signal_strength['bullish'] - signal_strength['bearish']

        # Only generate signal if strength is sufficient
        if abs(net_signal) < 0.3:
            return None

        signal_type = self._get_signal_type(0.5 + net_signal / 2)

        # Build reasoning
        reasoning_parts = []

        # RSI reasoning
        rsi = indicators['rsi']
        if rsi < 30:
            reasoning_parts.append(f"RSI oversold at {rsi:.1f}")
        elif rsi > 70:
            reasoning_parts.append(f"RSI overbought at {rsi:.1f}")

        # MACD reasoning
        macd = indicators['macd']
        if macd['histogram'] > 0:
            reasoning_parts.append("MACD bullish crossover")
        else:
            reasoning_parts.append("MACD bearish crossover")

        # Trend reasoning
        trend = analysis.analysis['trend']
        reasoning_parts.append(f"{trend} trend detected")

        # ADX reasoning
        if indicators['adx'] > 25:
            reasoning_parts.append(f"Strong trend (ADX: {indicators['adx']:.1f})")

        reasoning = "; ".join(reasoning_parts)

        # Estimate profit/loss targets based on ATR
        current_price = df['close'].iloc[-1]
        atr = indicators['atr']

        if signal_type in ['buy', 'strong_buy']:
            expected_profit = atr * 2  # 2x ATR profit target
            expected_loss = atr  # 1x ATR stop loss
        elif signal_type in ['sell', 'strong_sell']:
            expected_profit = atr * 2
            expected_loss = atr
        else:
            expected_profit = None
            expected_loss = None

        # Calculate priority based on signal strength
        priority = int(5 + (abs(net_signal) * 5))

        return AgentSignal(
            agent_name=self.name,
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal_type,
            confidence=analysis.confidence,
            reasoning=reasoning,
            data={
                'indicators': indicators,
                'signal_strength': signal_strength,
                'current_price': current_price
            },
            timeframe=timeframe,
            priority=priority,
            expected_profit=expected_profit,
            expected_loss=expected_loss
        )

    def _determine_trend(self, df: pd.DataFrame, indicators) -> str:
        """Determine overall market trend"""
        ma = indicators.moving_averages
        current_price = df['close'].iloc[-1]

        # Check moving average alignment
        if current_price > ma['sma_20'] > ma['sma_50']:
            return 'strong_uptrend'
        elif current_price > ma['sma_20']:
            return 'uptrend'
        elif current_price < ma['sma_20'] < ma['sma_50']:
            return 'strong_downtrend'
        elif current_price < ma['sma_20']:
            return 'downtrend'
        else:
            return 'sideways'
